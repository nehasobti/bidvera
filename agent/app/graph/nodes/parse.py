"""Node: Parse tender documents into structured sections and tables."""

from __future__ import annotations

import re
from typing import Any

from agent.app.graph.state import BidState
from agent.app.mcp_client import call_mcp_tool


async def parse_documents_node(state: BidState) -> dict[str, Any]:
    """Fetches and parses each attached document into structured sections."""
    bid_info = state.get("bid", {})
    tender_id = bid_info.get("tender_id", "")
    raw_docs = state.get("documents", [])

    parsed_docs: list[dict[str, Any]] = []

    for doc_meta in raw_docs:
        doc_id = doc_meta.get("id")
        doc_content = await call_mcp_tool(
            "tender_finder",
            "get_document",
            {"tender_id": tender_id, "doc_id": doc_id},
        )

        text = doc_content.get("text_content", "")

        # Split text into sections based on headers or numbered blocks
        sections: list[dict[str, Any]] = []
        raw_sections = re.split(r"\n(?=[0-9]+\.\s+[A-Z])", text)
        page_counter = 1

        for idx, sec_text in enumerate(raw_sections, start=1):
            sec_text = sec_text.strip()
            if not sec_text:
                continue

            lines = sec_text.split("\n", 1)
            heading = lines[0].strip() if len(lines) > 1 else f"Section {idx}"
            content = lines[1].strip() if len(lines) > 1 else lines[0]

            sections.append({
                "section_id": f"{doc_id}-sec-{idx}",
                "doc_name": doc_meta.get("name", ""),
                "heading": heading,
                "content": content,
                "page_ref": f"Page {page_counter}",
            })
            page_counter += max(1, len(sec_text) // 1500)

        # If no regex split occurred, provide whole text as one section
        if not sections and text:
            sections.append({
                "section_id": f"{doc_id}-sec-1",
                "doc_name": doc_meta.get("name", ""),
                "heading": "General Requirements",
                "content": text,
                "page_ref": "Page 1",
            })

        parsed_docs.append({
            "id": doc_id,
            "name": doc_meta.get("name", ""),
            "pages": doc_meta.get("pages", 1),
            "sections": sections,
            "tables_count": doc_content.get("tables_count", 0),
        })

    return {
        "documents": parsed_docs,
        "status": "parsed",
        "error": None,
    }
