"""FastAPI routes for starting, inspecting, streaming, and resuming bid workflows."""

from __future__ import annotations

import json
import uuid
from typing import Any

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from agent.app.graph.main_graph import bid_graph

router = APIRouter(prefix="/bids", tags=["bids"])


class StartBidRequest(BaseModel):
    """Payload to initiate a new bid workflow."""

    tender_id: str = Field(description="Target tender identifier (e.g. tender-001)")
    bid_id: str | None = Field(default=None, description="Optional custom bid thread ID")


class ResumeBidRequest(BaseModel):
    """Payload to resume a paused bid workflow."""

    decision: str = Field(default="bid", description="Human decision (e.g. bid, no_bid, approve)")
    comment: str = Field(default="", description="Reviewer commentary")
    who: str = Field(default="bid_manager", description="Reviewer username")


@router.post("", status_code=201)
async def start_bid(req: StartBidRequest) -> dict[str, Any]:
    """Start a new bid workflow thread."""
    bid_id = req.bid_id or f"bid-{uuid.uuid4().hex[:8]}"
    initial_state = {
        "bid": {
            "id": bid_id,
            "tender_id": req.tender_id,
            "status": "created",
        },
        "documents": [],
        "requirements": [],
        "eligibility": {},
        "decisions": [],
        "outline": [],
        "sections": [],
        "pricing": {},
        "review": {},
        "compliance_matrix": [],
        "artifacts": {},
        "status": "created",
        "error": None,
    }

    config = {"configurable": {"thread_id": bid_id}}
    # Execute graph up to checkpoint/completion
    result = await bid_graph.ainvoke(initial_state, config=config)

    return {
        "bid_id": bid_id,
        "tender_id": req.tender_id,
        "status": result.get("status", "running"),
        "title": result.get("bid", {}).get("title", ""),
        "requirements_count": len(result.get("requirements", [])),
        "eligibility_recommendation": result.get("eligibility", {}).get("recommendation", "unclear"),
    }


@router.get("/{bid_id}")
async def get_bid_status(bid_id: str) -> dict[str, Any]:
    """Retrieve current state and checkpoint progress of a bid thread."""
    config = {"configurable": {"thread_id": bid_id}}
    state_snapshot = bid_graph.get_state(config)

    if not state_snapshot or not state_snapshot.values:
        raise HTTPException(status_code=404, detail=f"Bid thread '{bid_id}' not found.")

    values = state_snapshot.values
    return {
        "bid_id": bid_id,
        "status": values.get("status", "unknown"),
        "bid": values.get("bid", {}),
        "documents_count": len(values.get("documents", [])),
        "requirements": values.get("requirements", []),
        "requirements_count": len(values.get("requirements", [])),
        "eligibility": values.get("eligibility", {}),
        "error": values.get("error"),
        "next": list(state_snapshot.next) if state_snapshot.next else [],
    }


@router.get("/{bid_id}/stream")
async def stream_bid_progress(bid_id: str) -> EventSourceResponse:
    """Stream live workflow execution progress events using Server-Sent Events (SSE)."""
    config = {"configurable": {"thread_id": bid_id}}

    async def event_generator():
        yield {
            "event": "connected",
            "data": json.dumps({"bid_id": bid_id, "status": "listening"}),
        }

        # Check existing state
        state_snapshot = bid_graph.get_state(config)
        if state_snapshot and state_snapshot.values:
            yield {
                "event": "state_snapshot",
                "data": json.dumps({
                    "status": state_snapshot.values.get("status", "running"),
                    "requirements_count": len(state_snapshot.values.get("requirements", [])),
                }),
            }

        # Stream node execution events
        async for event in bid_graph.astream_events(None, config=config, version="v2"):
            kind = event.get("event")
            name = event.get("name", "")

            if kind == "on_chain_start" and name in ("ingest", "parse_documents", "extract_section_requirements", "finalize_requirements", "check_eligibility"):
                yield {
                    "event": "node_started",
                    "data": json.dumps({"node": name}),
                }
            elif kind == "on_chain_end" and name in ("ingest", "parse_documents", "extract_section_requirements", "finalize_requirements", "check_eligibility"):
                yield {
                    "event": "node_finished",
                    "data": json.dumps({"node": name}),
                }

        yield {
            "event": "completed",
            "data": json.dumps({"bid_id": bid_id, "status": "done"}),
        }

    return EventSourceResponse(event_generator())


@router.post("/{bid_id}/resume")
async def resume_bid(bid_id: str, req: ResumeBidRequest) -> dict[str, Any]:
    """Resume execution of a bid thread from its latest checkpoint."""
    config = {"configurable": {"thread_id": bid_id}}
    state_snapshot = bid_graph.get_state(config)

    if not state_snapshot or not state_snapshot.values:
        raise HTTPException(status_code=404, detail=f"Bid thread '{bid_id}' not found.")

    # Continue execution
    result = await bid_graph.ainvoke(None, config=config)

    return {
        "bid_id": bid_id,
        "status": result.get("status", "resumed"),
        "requirements_count": len(result.get("requirements", [])),
        "eligibility_recommendation": result.get("eligibility", {}).get("recommendation", "unclear"),
    }
