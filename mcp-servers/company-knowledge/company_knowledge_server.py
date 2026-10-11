"""Company Knowledge MCP Server for Tychon Software.

Provides tools to retrieve company profile facts, search evidence chunks,
find relevant case studies, list valid certifications, and fetch CVs.
"""

from __future__ import annotations

import argparse
import os
from typing import Any

import uvicorn
from mcp.server.fastmcp import FastMCP
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response
from store import CompanyKnowledgeStore

SERVER_NAME = "company-knowledge"
SERVER_VERSION = "0.1.0"

store = CompanyKnowledgeStore()

mcp = FastMCP(
    name=SERVER_NAME,
    instructions="MCP Server for Tychon Software corporate knowledge, case studies, certifications, and CV retrieval."
)


@mcp.tool()
def get_profile() -> dict[str, Any]:
    """Retrieve official company corporate profile, legal entities, turnover, and capabilities.

    Returns:
        Structured company profile dictionary.
    """
    if store.profile:
        return store.profile.model_dump()
    return {"error": "Profile data not found."}


@mcp.tool()
def search_knowledge(
    query: str,
    doc_types: list[str] | None = None,
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Perform hybrid search over indexed company knowledge (case studies, past proposals, certs, CVs).

    Args:
        query: Semantic or keyword search query (e.g. 'cloud migration downtime SLA').
        doc_types: Optional filter by document type (e.g. ['case_study', 'past_proposal']).
        top_k: Maximum number of relevant chunks to return (default 5).

    Returns:
        Ranked list of knowledge chunks with citations and relevance scores.
    """
    chunks = store.search_hybrid(query=query, doc_types=doc_types, top_k=top_k)
    return [c.model_dump() for c in chunks]


@mcp.tool()
def find_case_studies(
    tags: list[str] | None = None,
    industry: str | None = None,
) -> list[dict[str, Any]]:
    """Find past delivery case studies filtered by technology tags or client industry.

    Args:
        tags: List of technology or methodology tags (e.g. ['aws', 'kubernetes', 'devops']).
        industry: Optional client industry filter (e.g. 'Transportation & Logistics', 'Healthcare').

    Returns:
        Matching case studies with challenges, solutions, and audited metrics.
    """
    results: list[dict[str, Any]] = []
    norm_tags = [t.lower().strip() for t in tags] if tags else []

    for cs in store.case_studies:
        if industry and industry.lower() not in cs.industry.lower():
            continue
        if norm_tags:
            cs_tags = [t.lower() for t in cs.tags]
            # Match any tag
            if not any(t in cs_tags for t in norm_tags):
                continue
        results.append(cs.model_dump())

    return results


@mcp.tool()
def list_certifications() -> list[dict[str, Any]]:
    """List organizational certifications, filtering out expired certificates from authoritative evidence.

    Returns:
        List of company certifications with accreditation body, validity dates, and status.
    """
    return [c.model_dump() for c in store.certifications]


@mcp.tool()
def get_cv(
    role: str | None = None,
    skills: list[str] | None = None,
) -> list[dict[str, Any]]:
    """Retrieve staff CV profiles by role title or technical skill set.

    Args:
        role: Key role keyword (e.g. 'Cloud Architect', 'DevOps', 'Security').
        skills: Specific skills to match (e.g. ['Kubernetes', 'Terraform']).

    Returns:
        List of matching staff CV profiles with certifications and project highlights.
    """
    results: list[dict[str, Any]] = []
    r_filter = role.lower().strip() if role else ""
    s_filter = [s.lower().strip() for s in skills] if skills else []

    for cv in store.cvs:
        if r_filter and r_filter not in cv.role.lower():
            continue
        if s_filter:
            cv_skills = [s.lower() for s in cv.skills]
            if not any(s in cv_skills for s in s_filter):
                continue
        results.append(cv.model_dump())

    return results


@mcp.resource("company://profile")
def company_profile_resource() -> str:
    """Markdown summary of Tychon Software corporate profile."""
    if not store.profile:
        return "# Company Profile Not Available"
    p = store.profile
    return (
        f"# {p.legal_name} ({p.trade_name})\n\n"
        f"- **Founded:** {p.founded_year} ({p.years_in_business} years in business)\n"
        f"- **EU Headquarters:** {p.headquarters['eu']['address']}\n"
        f"- **India Headquarters:** {p.headquarters['india']['address']}\n"
        f"- **DUNS:** `{p.duns_number}`\n"
        f"- **Headcount:** {p.workforce['total_full_time_employees']} full-time engineers & consultants\n"
        f"- **Latest Annual Turnover:** €{p.financials['turnover'][0]['turnover_eur']:,}\n\n"
        f"## Core Competencies\n\n"
        + "\n".join([f"- {c}" for c in p.core_competencies])
        + f"\n\n## Overview\n\n{p.overview}\n"
    )


@mcp.prompt()
def company_voice() -> str:
    """Style guide and tone of voice for drafting tender responses on behalf of Tychon Software."""
    return (
        "You are writing technical proposal responses on behalf of Tychon Software.\n\n"
        "Guidelines:\n"
        "1. Tone: Confident, precise, engineering-driven, professional, and compliant with EU/international procurement standards.\n"
        "2. Grounding: NEVER state facts, metrics, client names, certifications, or employee credentials without citing an explicit knowledge chunk.\n"
        "3. Identity: Use 'Tychon Software' in opening paragraphs rather than an ambiguous 'we'.\n"
        "4. Evidence: Always pair architectural claims with demonstrated case study metrics (e.g. 'zero unplanned downtime across 450 VMs in CS-001').\n"
        "5. Missing Information: If required data is unavailable, insert '[NEEDS INPUT: <description of missing item>]'. Never fabricate."
    )


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Enforces Bearer token auth for MCP endpoints when MCP_AUTH_TOKEN is set."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if request.url.path in ("/health", "/"):
            return await call_next(request)

        expected_token = os.environ.get("MCP_AUTH_TOKEN") or os.environ.get("COMPANY_KNOWLEDGE_AUTH_TOKEN")
        if expected_token:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer ") or auth_header[7:].strip() != expected_token:
                return JSONResponse(
                    {"error": "Unauthorized: Invalid or missing Bearer token"},
                    status_code=401,
                )

        return await call_next(request)


def create_asgi_app() -> Any:
    """Builds ASGI Starlette app with middleware and health endpoint."""
    app = mcp.sse_app()
    app.add_middleware(BearerAuthMiddleware)

    async def health_endpoint(_: Request) -> JSONResponse:
        return JSONResponse(
            {
                "status": "healthy",
                "server": SERVER_NAME,
                "version": SERVER_VERSION,
                "indexed_chunks": len(store.chunks),
                "certifications_count": len(store.certifications),
                "case_studies_count": len(store.case_studies),
            }
        )

    app.add_route("/health", health_endpoint, methods=["GET"])
    return app


def main() -> None:
    parser = argparse.ArgumentParser(description=f"{SERVER_NAME} MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "http"], default="sse")
    parser.add_argument("--host", default=os.environ.get("MCP_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8002")))
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        app = create_asgi_app()
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
