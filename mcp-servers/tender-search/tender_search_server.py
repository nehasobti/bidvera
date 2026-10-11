"""Tender Search MCP Server.

Provides tools to search tenders, fetch details, list associated documents,
and extract document contents.
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
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from tender_models import TenderDocumentContent, TenderDocumentInfo, TenderItem

SERVER_NAME = "tender-search"
SERVER_VERSION = "0.1.0"

# Locate sample-data/tenders
def get_tenders_dir() -> Path:
    env_dir = os.environ.get("TENDERS_DATA_DIR")
    if env_dir and Path(env_dir).exists():
        return Path(env_dir)
    # Relative fallbacks
    candidates = [
        Path.cwd() / "sample-data" / "tenders",
        Path(__file__).resolve().parent.parent.parent / "sample-data" / "tenders",
        Path(__file__).resolve().parent / "data",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


def load_registry() -> list[TenderItem]:
    tenders_dir = get_tenders_dir()
    registry_file = tenders_dir / "tenders_registry.json"
    if not registry_file.exists():
        return []
    with open(registry_file, encoding="utf-8") as f:
        data = json.load(f)
    items: list[TenderItem] = []
    for item in data:
        docs = [
            TenderDocumentInfo(
                id=d["id"],
                name=d["name"],
                type=d.get("type", "general"),
                pages=d.get("pages", 1),
                file_path=str(tenders_dir / item["id"] / d["name"])
            )
            for d in item.get("documents", [])
        ]
        items.append(
            TenderItem(
                id=item["id"],
                title=item["title"],
                buyer=item["buyer"],
                country=item["country"],
                category=item["category"],
                deadline=item["deadline"],
                estimated_budget_eur=item.get("estimated_budget_eur"),
                summary=item["summary"],
                documents=docs,
                eligibility_criteria=item.get("eligibility_criteria", [])
            )
        )
    return items


# Initialize FastMCP Server
mcp = FastMCP(
    name=SERVER_NAME,
    instructions="MCP Server for tender discovery, metadata retrieval, and RFP document parsing."
)


@mcp.tool()
def search_tenders(
    query: str = "",
    country: str | None = None,
    category: str | None = None,
    deadline_after: str | None = None,
) -> list[dict[str, Any]]:
    """Search for relevant tenders using keyword matching and filters.

    Args:
        query: Search keywords in title, summary, or buyer.
        country: Country or economic region code (e.g. EU, Germany, India).
        category: Procurement category (e.g. Cloud Migration, Data & AI).
        deadline_after: Filter tenders with deadline strictly after this ISO date.

    Returns:
        List of matching tender summaries.
    """
    items = load_registry()
    results: list[dict[str, Any]] = []
    q = query.lower().strip()

    cutoff_date: datetime.datetime | None = None
    if deadline_after:
        try:
            cutoff_date = datetime.datetime.fromisoformat(deadline_after.replace("Z", "+00:00"))
        except ValueError:
            pass

    for item in items:
        if q and not (q in item.title.lower() or q in item.summary.lower() or q in item.buyer.lower()):
            continue
        if country and country.lower() not in item.country.lower():
            continue
        if category and category.lower() not in item.category.lower():
            continue
        if cutoff_date:
            try:
                item_deadline = datetime.datetime.fromisoformat(item.deadline.replace("Z", "+00:00"))
                if item_deadline <= cutoff_date:
                    continue
            except ValueError:
                pass

        results.append(item.model_dump())

    return results


@mcp.tool()
def get_tender(tender_id: str) -> dict[str, Any]:
    """Retrieve full details, scope, and eligibility criteria for a specific tender.

    Args:
        tender_id: The tender identifier (e.g. tender-001).

    Returns:
        Full tender item object, or error dict if not found.
    """
    items = load_registry()
    for item in items:
        if item.id == tender_id:
            return item.model_dump()
    return {"error": f"Tender '{tender_id}' not found."}


@mcp.tool()
def list_documents(tender_id: str) -> list[dict[str, Any]]:
    """List all documents associated with a tender.

    Args:
        tender_id: The tender identifier (e.g. tender-001).

    Returns:
        List of document metadata items.
    """
    tender = get_tender(tender_id)
    if "error" in tender:
        return []
    return [doc for doc in tender.get("documents", [])]


@mcp.tool()
def get_document(tender_id: str, doc_id: str) -> dict[str, Any]:
    """Extract and return text and structural contents of a tender document.

    Args:
        tender_id: The parent tender ID.
        doc_id: The document ID (e.g. doc-001-main).

    Returns:
        Extracted document text, section count, and metadata.
    """
    docs = list_documents(tender_id)
    target_doc = next((d for d in docs if d["id"] == doc_id), None)
    if not target_doc:
        return {"error": f"Document '{doc_id}' for tender '{tender_id}' not found."}

    file_path = Path(target_doc["file_path"])
    if not file_path.exists():
        # Try finding in tender folder
        file_path = get_tenders_dir() / tender_id / target_doc["name"]

    if not file_path.exists():
        return {"error": f"Document file '{target_doc['name']}' not found on disk."}

    text_content = ""
    sections_count = 0
    tables_count = 0

    if file_path.suffix.lower() == ".docx":
        try:
            doc = docx.Document(file_path)
            paragraphs_text: list[str] = []
            for p in doc.paragraphs:
                if p.text.strip():
                    paragraphs_text.append(p.text)
                    if p.style and "Heading" in p.style.name:
                        sections_count += 1
            tables_count = len(doc.tables)
            for table in doc.tables:
                table_lines: list[str] = []
                for row in table.rows:
                    row_cells = [cell.text.strip() for cell in row.cells]
                    table_lines.append(" | ".join(row_cells))
                paragraphs_text.append("\n[TABLE]\n" + "\n".join(table_lines) + "\n[/TABLE]")
            text_content = "\n\n".join(paragraphs_text)
        except Exception as e:
            text_content = f"Error reading docx: {e}"
    else:
        try:
            with open(file_path, encoding="utf-8") as f:
                text_content = f.read()
        except Exception as e:
            text_content = f"Error reading text: {e}"

    res = TenderDocumentContent(
        tender_id=tender_id,
        doc_id=doc_id,
        name=target_doc["name"],
        content_type=file_path.suffix.lstrip("."),
        text_content=text_content,
        sections_count=sections_count,
        tables_count=tables_count,
    )
    return res.model_dump()


@mcp.resource("tender://{tender_id}/summary")
def tender_summary_resource(tender_id: str) -> str:
    """Markdown summary of a tender."""
    tender = get_tender(tender_id)
    if "error" in tender:
        return f"# Tender Not Found\n\nTender `{tender_id}` does not exist."
    return (
        f"# {tender['title']}\n\n"
        f"- **Tender ID:** `{tender['id']}`\n"
        f"- **Buyer:** {tender['buyer']}\n"
        f"- **Country:** {tender['country']}\n"
        f"- **Category:** {tender['category']}\n"
        f"- **Deadline:** {tender['deadline']}\n"
        f"- **Estimated Budget:** €{tender.get('estimated_budget_eur', 0):,}\n\n"
        f"## Summary\n\n{tender['summary']}\n"
    )


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Enforces Bearer token auth for MCP endpoints when MCP_AUTH_TOKEN is configured."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if request.url.path in ("/health", "/"):
            return await call_next(request)

        expected_token = os.environ.get("MCP_AUTH_TOKEN") or os.environ.get("TENDER_SEARCH_AUTH_TOKEN")
        if expected_token:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer ") or auth_header[7:].strip() != expected_token:
                return JSONResponse(
                    {"error": "Unauthorized: Invalid or missing Bearer token"},
                    status_code=401,
                )

        return await call_next(request)


def create_asgi_app() -> Any:
    """Constructs the ASGI app with middleware and health check."""
    app = mcp.sse_app()
    app.add_middleware(BearerAuthMiddleware)

    async def health_endpoint(_: Request) -> JSONResponse:
        return JSONResponse(
            {
                "status": "healthy",
                "server": SERVER_NAME,
                "version": SERVER_VERSION,
                "tenders_count": len(load_registry()),
            }
        )

    app.add_route("/health", health_endpoint, methods=["GET"])
    return app


def main() -> None:
    parser = argparse.ArgumentParser(description=f"{SERVER_NAME} MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "http"], default="sse")
    parser.add_argument("--host", default=os.environ.get("MCP_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8001")))
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        app = create_asgi_app()
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
