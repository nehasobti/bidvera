"""Node: Ingest tender specifications and list attached documents."""

from __future__ import annotations

from typing import Any

from agent.app.graph.state import BidState
from agent.app.mcp_client import call_mcp_tool


async def ingest_node(state: BidState) -> dict[str, Any]:
    """Ingests tender metadata and document catalog using tender-search MCP server."""
    bid_info = state.get("bid", {})
    tender_id = bid_info.get("tender_id")
    if not tender_id:
        return {"status": "error", "error": "No tender_id provided in bid state"}

    # 1. Fetch tender details
    tender_data = await call_mcp_tool("tender_finder", "get_tender", {"tender_id": tender_id})
    if "error" in tender_data:
        return {"status": "error", "error": tender_data["error"]}

    # 2. Fetch document list
    docs = await call_mcp_tool("tender_finder", "list_documents", {"tender_id": tender_id})

    # Update state
    updated_bid = dict(bid_info)
    updated_bid.update({
        "title": tender_data.get("title", ""),
        "buyer": tender_data.get("buyer", ""),
        "country": tender_data.get("country", ""),
        "category": tender_data.get("category", ""),
        "deadline": tender_data.get("deadline", ""),
        "summary": tender_data.get("summary", ""),
        "eligibility_criteria": tender_data.get("eligibility_criteria", []),
        "status": "ingested",
    })

    return {
        "bid": updated_bid,
        "documents": docs,
        "status": "ingested",
        "error": None,
    }
