"""Node and parallel Send fanout for requirement extraction."""

from __future__ import annotations

import json
import re
from typing import Any

from langchain_core.messages import HumanMessage, SystemMessage
from langgraph.types import Send

from agent.app.core.llm import get_llm
from agent.app.graph.state import BidState


def fanout_sections(state: BidState) -> list[Send]:
    """Generates parallel Send branches for each parsed section across all documents."""
    docs = state.get("documents", [])
    sends: list[Send] = []

    for doc in docs:
        sections = doc.get("sections", [])
        for sec in sections:
            sends.append(
                Send(
                    "extract_section_requirements",
                    {
                        "section": sec,
                        "tender_id": state.get("bid", {}).get("tender_id", ""),
                    },
                )
            )

    # Fallback if no sections were parsed
    if not sends:
        sends.append(
            Send(
                "extract_section_requirements",
                {
                    "section": {
                        "section_id": "fallback-1",
                        "heading": "General Scope",
                        "content": state.get("bid", {}).get("summary", ""),
                        "page_ref": "Page 1",
                    },
                    "tender_id": state.get("bid", {}).get("tender_id", ""),
                },
            )
        )

    return sends


async def extract_section_requirements(payload: dict[str, Any]) -> dict[str, Any]:
    """Worker node that extracts atomic requirements from a single document section."""
    sec = payload.get("section", {})
    sec_heading = sec.get("heading", "")
    sec_content = sec.get("content", "")
    page_ref = sec.get("page_ref", "Page 1")

    # 1. First parse any structured table rows if present in the text
    extracted: list[dict[str, Any]] = []
    if "[TABLE]" in sec_content:
        table_matches = re.findall(r"\[TABLE\](.*?)\[/TABLE\]", sec_content, re.DOTALL)
        for tbl in table_matches:
            lines = [line.strip() for line in tbl.strip().split("\n") if line.strip()]
            for line in lines[1:]:  # skip header row
                cols = [c.strip() for c in line.split("|")]
                if len(cols) >= 3 and cols[0].startswith("REQ-"):
                    req_type = "Mandatory" if "mandatory" in cols[2].lower() else "Scored"
                    extracted.append({
                        "id": cols[0],
                        "text": cols[1],
                        "type": req_type,
                        "weight": cols[3] if len(cols) > 3 else "Pass/Fail",
                        "section": sec_heading,
                        "page_ref": page_ref,
                        "category": "technical",
                    })

    # 2. If table didn't yield requirements, call LLM to extract requirements
    if not extracted:
        llm = get_llm("fast")
        system_prompt = (
            "You are an expert procurement analyst. Extract all atomic requirements from the following "
            "RFP section. Return a JSON object with key 'requirements', containing a list of objects with "
            "id, text, type (Mandatory/Scored/Optional), weight, section, page_ref, and category."
        )
        user_prompt = f"Section: {sec_heading}\nPage: {page_ref}\nContent:\n{sec_content}"

        response = await llm.ainvoke([
            SystemMessage(content=system_prompt),
            HumanMessage(content=user_prompt),
        ])

        try:
            parsed = json.loads(str(response.content))
            raw_reqs = parsed.get("requirements", [])
            for r in raw_reqs:
                extracted.append({
                    "id": r.get("id", f"REQ-{len(extracted)+1:03d}"),
                    "text": r.get("text", ""),
                    "type": r.get("type", "Mandatory"),
                    "weight": r.get("weight", "Pass/Fail"),
                    "section": sec_heading,
                    "page_ref": page_ref,
                    "category": r.get("category", "technical"),
                })
        except Exception:
            pass

    return {"requirements": extracted}


async def finalize_requirements_node(state: BidState) -> dict[str, Any]:
    """Consolidates and orders merged requirements."""
    reqs = state.get("requirements", [])
    # Sort with Mandatory first, then Scored, then Optional
    type_priority = {"Mandatory": 0, "Scored": 1, "Optional": 2}
    sorted_reqs = sorted(reqs, key=lambda r: (type_priority.get(r.get("type", "Mandatory"), 3), r.get("id", "")))

    return {
        "requirements": sorted_reqs,
        "status": "requirements_extracted",
    }
