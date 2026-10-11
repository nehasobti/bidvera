"""Documents MCP Server.

Provides tools for generating proposal DOCX documents from structured bid state,
appending compliance matrices, converting to PDF, and serving download references.
"""

from __future__ import annotations

import argparse
import datetime
import json
import os
from pathlib import Path
from typing import Any

import docx
import uvicorn
from document_models import (
    BidDocumentInput,
    DocumentDownloadInfo,
    DocumentGenerationResult,
    PdfConversionResult,
)
from generator import (
    add_compliance_table_to_doc,
    build_docx_proposal,
    convert_docx_to_pdf,
)
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

SERVER_NAME = "documents"
SERVER_VERSION = "0.1.0"


def get_output_dir() -> Path:
    env_dir = os.environ.get("DOCUMENTS_OUTPUT_DIR")
    if env_dir:
        p = Path(env_dir)
        p.mkdir(parents=True, exist_ok=True)
        return p
    candidates = [
        Path.cwd() / "output" / "documents",
        Path(__file__).resolve().parent.parent.parent / "output" / "documents",
        Path(__file__).resolve().parent / "output",
    ]
    p = candidates[0]
    p.mkdir(parents=True, exist_ok=True)
    return p


# In-memory document registry: doc_id -> metadata
DOC_REGISTRY: dict[str, dict[str, Any]] = {}

mcp = FastMCP(
    name=SERVER_NAME,
    instructions="MCP Server for proposal document generation, compliance matrices, and PDF conversion."
)


@mcp.tool()
def create_response_doc(
    bid_json: dict[str, Any] | str,
    template: str = "standard",
) -> dict[str, Any]:
    """Generate a formal technical and commercial response document (.docx) from bid state.

    Args:
        bid_json: Bid state dictionary or serialized JSON string containing title, buyer, sections, pricing, etc.
        template: Design template variant ('standard', 'executive', 'technical').

    Returns:
        Generated document metadata including file path, doc_id, and size.
    """
    if isinstance(bid_json, str):
        try:
            bid_data = json.loads(bid_json)
        except Exception as e:
            return {"error": f"Invalid JSON payload: {e}"}
    else:
        bid_data = bid_json

    bid_input = BidDocumentInput(**bid_data)
    doc_id = f"doc-{bid_input.bid_id}-{int(datetime.datetime.now().timestamp())}"
    output_dir = get_output_dir()
    file_name = f"Proposal_{bid_input.bid_id}_{bid_input.tender_id}.docx"
    docx_path = output_dir / file_name

    saved_path = build_docx_proposal(bid=bid_input, output_path=docx_path)
    size_bytes = saved_path.stat().st_size

    info = DocumentGenerationResult(
        doc_id=doc_id,
        bid_id=bid_input.bid_id,
        docx_path=str(saved_path),
        docx_size_bytes=size_bytes,
        created_at=datetime.datetime.now().isoformat(),
        template_used=template,
    )

    DOC_REGISTRY[doc_id] = {
        "doc_id": doc_id,
        "bid_id": bid_input.bid_id,
        "docx_path": str(saved_path),
        "pdf_path": None,
        "created_at": info.created_at,
    }

    return info.model_dump()


@mcp.tool()
def add_compliance_matrix(
    doc_id: str,
    matrix: list[dict[str, Any]],
) -> dict[str, Any]:
    """Append or refresh a structured compliance matrix table in an existing DOCX document.

    Args:
        doc_id: The unique document identifier returned from create_response_doc.
        matrix: List of compliance requirement dicts (req_id, description, compliance_status, etc.).

    Returns:
        Updated document status and size.
    """
    doc_meta = DOC_REGISTRY.get(doc_id)
    if not doc_meta or not doc_meta.get("docx_path"):
        return {"error": f"Document ID '{doc_id}' not found in registry."}

    docx_path = Path(doc_meta["docx_path"])
    if not docx_path.exists():
        return {"error": f"File '{docx_path}' does not exist on disk."}

    doc = docx.Document(docx_path)
    add_compliance_table_to_doc(doc, matrix, section_index=6)
    doc.save(docx_path)

    updated_size = docx_path.stat().st_size
    return {
        "doc_id": doc_id,
        "status": "compliance_matrix_appended",
        "matrix_entries_count": len(matrix),
        "docx_path": str(docx_path),
        "docx_size_bytes": updated_size,
    }


@mcp.tool()
def convert_to_pdf(doc_id: str) -> dict[str, Any]:
    """Convert generated DOCX proposal document into a distribution-ready PDF file.

    Args:
        doc_id: The document identifier.

    Returns:
        PDF conversion result with path, file size, and converter engine used.
    """
    doc_meta = DOC_REGISTRY.get(doc_id)
    if not doc_meta or not doc_meta.get("docx_path"):
        return {"error": f"Document ID '{doc_id}' not found in registry."}

    docx_path = Path(doc_meta["docx_path"])
    if not docx_path.exists():
        return {"error": f"DOCX file '{docx_path}' not found on disk."}

    pdf_path = docx_path.with_suffix(".pdf")
    final_pdf_path, engine = convert_docx_to_pdf(docx_path=docx_path, output_pdf_path=pdf_path)

    doc_meta["pdf_path"] = str(final_pdf_path)
    size_bytes = final_pdf_path.stat().st_size

    res = PdfConversionResult(
        doc_id=doc_id,
        pdf_path=str(final_pdf_path),
        pdf_size_bytes=size_bytes,
        converter_engine=engine,
    )
    return res.model_dump()


@mcp.tool()
def get_download_url(doc_id: str) -> dict[str, Any]:
    """Retrieve download file paths and availability for DOCX and PDF artifacts.

    Args:
        doc_id: Document ID.

    Returns:
        Paths, sizes, and file download indicators for both DOCX and PDF.
    """
    doc_meta = DOC_REGISTRY.get(doc_id)
    if not doc_meta:
        return {"error": f"Document ID '{doc_id}' not found in registry."}

    docx_path_str = doc_meta.get("docx_path")
    docx_path = Path(docx_path_str) if docx_path_str else None
    docx_exists = docx_path.exists() if docx_path else False
    docx_size = docx_path.stat().st_size if docx_exists and docx_path else 0

    pdf_path_str = doc_meta.get("pdf_path")
    pdf_path = Path(pdf_path_str) if pdf_path_str else None
    pdf_exists = pdf_path.exists() if pdf_path else False
    pdf_size = pdf_path.stat().st_size if pdf_exists and pdf_path else 0

    res = DocumentDownloadInfo(
        doc_id=doc_id,
        docx_path=docx_path_str,
        docx_exists=docx_exists,
        docx_size_bytes=docx_size,
        pdf_path=pdf_path_str,
        pdf_exists=pdf_exists,
        pdf_size_bytes=pdf_size,
        download_url_docx=f"/api/documents/{doc_id}/download/docx",
        download_url_pdf=f"/api/documents/{doc_id}/download/pdf",
    )
    return res.model_dump()


@mcp.prompt()
def final_checklist() -> str:
    """Pre-dispatch quality and completeness checklist prompt for proposal reviewers."""
    return (
        "Final Proposal Quality & Verification Checklist:\n"
        "1. Mandatory Compliance: Every mandatory requirement in the compliance matrix has status 'Compliant' and links to a specific proposal section.\n"
        "2. Grounded Claims: Every technical claim, customer metric, and certification cites an audited chunk.\n"
        "3. Pricing Consistency: Effort totals in the executive narrative exactly match the approved commercial price sheet.\n"
        "4. No Placeholders: Verify that zero '[NEEDS INPUT: ...]' tokens remain in any draft section.\n"
        "5. Authorized Signatures: Confirm authorized corporate signatories (Markus Weber / Elena Rostova) are present."
    )


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Enforces Bearer token auth for MCP endpoints when MCP_AUTH_TOKEN is configured."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if request.url.path in ("/health", "/"):
            return await call_next(request)

        expected_token = os.environ.get("MCP_AUTH_TOKEN") or os.environ.get("DOCUMENTS_AUTH_TOKEN")
        if expected_token:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer ") or auth_header[7:].strip() != expected_token:
                return JSONResponse(
                    {"error": "Unauthorized: Invalid or missing Bearer token"},
                    status_code=401,
                )

        return await call_next(request)


def create_asgi_app() -> Any:
    """Builds ASGI Starlette app with middleware and health check."""
    app = mcp.sse_app()
    app.add_middleware(BearerAuthMiddleware)

    async def health_endpoint(_: Request) -> JSONResponse:
        return JSONResponse(
            {
                "status": "healthy",
                "server": SERVER_NAME,
                "version": SERVER_VERSION,
                "documents_generated": len(DOC_REGISTRY),
            }
        )

    app.add_route("/health", health_endpoint, methods=["GET"])
    return app


def main() -> None:
    parser = argparse.ArgumentParser(description=f"{SERVER_NAME} MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "http"], default="sse")
    parser.add_argument("--host", default=os.environ.get("MCP_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8004")))
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        app = create_asgi_app()
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
