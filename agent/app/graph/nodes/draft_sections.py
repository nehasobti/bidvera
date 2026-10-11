"""Parallel Section Drafting Nodes for Bidvera.

Fans out to draft each section in parallel using company knowledge,
past case studies, and mapped requirements.
"""

from __future__ import annotations

import operator
from typing import Any
from langgraph.types import Send
from pydantic import BaseModel, Field

from agent.app.core.llm import get_llm
from agent.app.graph.state import BidState
from agent.app.mcp_client import call_fastmcp_tool


class SectionDraftInput(BaseModel):
    """Payload passed to an individual parallel section drafting branch."""

    bid_id: str
    tender_id: str
    section_id: str
    title: str
    description: str
    mapped_requirements: list[str] = Field(default_factory=list)
    target_pages: int = 2
    tender_title: str = ""
    buyer: str = ""


async def fanout_sections_for_drafting(state: BidState) -> list[Send]:
    """Conditional edge: fans out to draft all outline sections in parallel."""
    outline = state.get("outline", [])
    bid_info = state.get("bid", {})
    bid_id = bid_info.get("id", "bid-default")
    tender_id = bid_info.get("tender_id", "tender-001")
    tender_title = bid_info.get("title", "")
    buyer = bid_info.get("buyer", "")

    sends: list[Send] = []
    for sec in outline:
        payload = SectionDraftInput(
            bid_id=bid_id,
            tender_id=tender_id,
            section_id=sec.get("id", "sec-001"),
            title=sec.get("title", "Section"),
            description=sec.get("description", ""),
            mapped_requirements=sec.get("mapped_requirements", []),
            target_pages=sec.get("target_pages", 2),
            tender_title=tender_title,
            buyer=buyer,
        )
        sends.append(Send("draft_section", payload.model_dump()))

    return sends


async def draft_section_node(payload: dict[str, Any]) -> dict[str, Any]:
    """Draft a single proposal section grounded in company knowledge and case studies."""
    section_id = payload.get("section_id", "sec-1")
    title = payload.get("title", "Section")
    desc = payload.get("description", "")
    mapped_reqs = payload.get("mapped_requirements", [])
    buyer = payload.get("buyer", "the Client")
    tender_title = payload.get("tender_title", "the RFP")

    # Fetch relevant company knowledge based on section title
    evidence_text = ""
    try:
        if "Security" in title or "Compliance" in title:
            certs = await call_fastmcp_tool("company-knowledge", "get_certifications", {})
            evidence_text = f"Corporate Certifications: {certs}"
        elif "Team" in title or "Past Performance" in title:
            cases = await call_fastmcp_tool("company-knowledge", "get_case_studies", {})
            evidence_text = f"Verified Case Studies: {cases}"
        else:
            profile = await call_fastmcp_tool("company-knowledge", "get_company_profile", {})
            evidence_text = f"Company Profile: {profile}"
    except Exception:
        evidence_text = "Tychon Software: Enterprise Cloud & DevOps delivery partner with ISO 27001 accreditation."

    llm = get_llm()
    system_prompt = (
        "You are an expert bid proposal writer for Tychon Software. Write professional, winning, "
        "evidence-backed proposal text. Adhere strictly to the requested section and mapped requirements. "
        "Do NOT hallucinate client names or facts beyond the provided context."
    )
    user_prompt = (
        f"Section Title: {title}\n"
        f"Description: {desc}\n"
        f"Buyer: {buyer}\n"
        f"Tender: {tender_title}\n"
        f"Mapped Requirements: {', '.join(mapped_reqs) if mapped_reqs else 'General'}\n\n"
        f"Company Evidence & Facts:\n{evidence_text}\n\n"
        "Draft a comprehensive, structured response (4-6 paragraphs with bullet points and clear methodology)."
    )

    response = await llm.ainvoke([
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_prompt},
    ])

    content_text = response.content if hasattr(response, "content") else str(response)

    drafted_section = {
        "section_id": section_id,
        "title": title,
        "content": content_text,
        "mapped_requirements": mapped_reqs,
        "word_count": len(content_text.split()),
        "status": "drafted",
    }

    return {"sections": [drafted_section]}


async def finalize_drafting_node(state: BidState) -> dict[str, Any]:
    """Aggregate drafted sections, sort by section order, and update bid status."""
    sections = state.get("sections", [])
    outline = state.get("outline", [])

    # Order sections according to the original outline order
    outline_order = {sec.get("id"): idx for idx, sec in enumerate(outline)}
    sorted_sections = sorted(sections, key=lambda s: outline_order.get(s.get("section_id"), 99))

    return {
        "sections": sorted_sections,
        "status": "sections_drafted",
    }
