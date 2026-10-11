"""FastAPI routes for starting, inspecting, streaming, and approving bid workflows."""

from __future__ import annotations

import json
import uuid
from pathlib import Path
from typing import Any
from fastapi import APIRouter, HTTPException
from langgraph.types import Command
from pydantic import BaseModel, Field
from sse_starlette.sse import EventSourceResponse

from agent.app.graph.main_graph import bid_graph

router = APIRouter(prefix="/bids", tags=["bids"])

# Persistent registry of thread IDs stored in data/bids_registry.json
REGISTRY_FILE = Path.cwd() / "data" / "bids_registry.json"


def _load_registry() -> dict[str, dict[str, Any]]:
    if REGISTRY_FILE.exists():
        try:
            with open(REGISTRY_FILE, encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}


def _save_registry(reg: dict[str, dict[str, Any]]) -> None:
    REGISTRY_FILE.parent.mkdir(parents=True, exist_ok=True)
    try:
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(reg, f, indent=2)
    except Exception:
        pass


BIDS_REGISTRY: dict[str, dict[str, Any]] = _load_registry()


class StartBidRequest(BaseModel):
    """Payload to initiate a new bid workflow."""

    tender_id: str = Field(description="Target tender identifier (e.g. tender-001)")
    bid_id: str | None = Field(default=None, description="Optional custom bid thread ID")


class SubmitDecisionRequest(BaseModel):
    """Payload to submit human checkpoint decision."""

    decision: str = Field(description="Human decision: 'bid' or 'no-bid'")
    comment: str = Field(default="", description="Reviewer commentary")
    who: str = Field(default="bid_manager", description="Reviewer identifier")


@router.get("")
@router.get("/")
async def list_bids() -> list[dict[str, Any]]:
    """List all tracked bids with their current status and progress."""
    registry = _load_registry()
    results: list[dict[str, Any]] = []
    for bid_id, meta in list(registry.items()):
        config = {"configurable": {"thread_id": bid_id}}
        snapshot = bid_graph.get_state(config)
        if snapshot and snapshot.values:
            val = snapshot.values
            is_waiting = any(t.interrupts for t in snapshot.tasks) if snapshot.tasks else False
            results.append({
                "bid_id": bid_id,
                "tender_id": meta.get("tender_id", ""),
                "title": val.get("bid", {}).get("title", meta.get("title", "")),
                "buyer": val.get("bid", {}).get("buyer", ""),
                "deadline": val.get("bid", {}).get("deadline", ""),
                "status": val.get("status", "running"),
                "is_waiting_for_approval": is_waiting,
                "requirements_count": len(val.get("requirements", [])),
                "eligibility_recommendation": val.get("eligibility", {}).get("recommendation", "unclear"),
                "has_outline": len(val.get("outline", [])) > 0,
                "sections_count": len(val.get("sections", [])),
                "total_price": val.get("pricing", {}).get("total_price"),
                "currency": val.get("pricing", {}).get("currency", "EUR"),
            })
    return results


@router.get("/approvals/inbox")
async def get_approvals_inbox() -> list[dict[str, Any]]:
    """Inbox returning all bids currently paused waiting for human checkpoint decisions."""
    inbox: list[dict[str, Any]] = []
    registry = _load_registry()
    for bid_id, meta in list(registry.items()):
        config = {"configurable": {"thread_id": bid_id}}
        snapshot = bid_graph.get_state(config)
        if snapshot and snapshot.tasks:
            for task in snapshot.tasks:
                if task.interrupts:
                    for interrupt_item in task.interrupts:
                        inbox.append({
                            "bid_id": bid_id,
                            "tender_id": meta.get("tender_id", ""),
                            "title": snapshot.values.get("bid", {}).get("title", ""),
                            "checkpoint": task.name,
                            "interrupt_payload": interrupt_item.value,
                            "created_at": snapshot.created_at if hasattr(snapshot, "created_at") else "",
                        })
    return inbox


@router.post("", status_code=201)
@router.post("/", status_code=201)
async def start_bid(req: StartBidRequest) -> dict[str, Any]:
    """Start a new bid workflow thread, running until first human checkpoint (bid_decision)."""
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
    registry = _load_registry()
    registry[bid_id] = {
        "bid_id": bid_id,
        "tender_id": req.tender_id,
        "title": req.tender_id,
    }
    _save_registry(registry)

    # Execute graph up to interrupt checkpoint
    result = await bid_graph.ainvoke(initial_state, config=config)

    snapshot = bid_graph.get_state(config)
    is_waiting = any(t.interrupts for t in snapshot.tasks) if snapshot.tasks else False
    interrupt_data = snapshot.tasks[0].interrupts[0].value if is_waiting and snapshot.tasks[0].interrupts else None

    # Update registry with actual title
    if "bid" in result and "title" in result["bid"]:
        registry[bid_id]["title"] = result["bid"]["title"]
        _save_registry(registry)

    return {
        "bid_id": bid_id,
        "tender_id": req.tender_id,
        "status": result.get("status", "running"),
        "title": result.get("bid", {}).get("title", ""),
        "buyer": result.get("bid", {}).get("buyer", ""),
        "requirements_count": len(result.get("requirements", [])),
        "eligibility_recommendation": result.get("eligibility", {}).get("recommendation", "unclear"),
        "is_waiting_for_approval": is_waiting,
        "pending_checkpoint": interrupt_data,
    }


@router.get("/{bid_id}")
async def get_bid_status(bid_id: str) -> dict[str, Any]:
    """Retrieve state, requirements, eligibility, outline, and pending human decisions."""
    config = {"configurable": {"thread_id": bid_id}}
    state_snapshot = bid_graph.get_state(config)

    if not state_snapshot or not state_snapshot.values:
        raise HTTPException(status_code=404, detail=f"Bid thread '{bid_id}' not found.")

    values = state_snapshot.values
    is_waiting = any(t.interrupts for t in state_snapshot.tasks) if state_snapshot.tasks else False
    interrupt_payload = (
        state_snapshot.tasks[0].interrupts[0].value
        if is_waiting and state_snapshot.tasks and state_snapshot.tasks[0].interrupts
        else None
    )

    return {
        "bid_id": bid_id,
        "status": values.get("status", "unknown"),
        "bid": values.get("bid", {}),
        "documents": values.get("documents", []),
        "documents_count": len(values.get("documents", [])),
        "requirements": values.get("requirements", []),
        "requirements_count": len(values.get("requirements", [])),
        "eligibility": values.get("eligibility", {}),
        "outline": values.get("outline", []),
        "sections": values.get("sections", []),
        "pricing": values.get("pricing", {}),
        "compliance_matrix": values.get("compliance_matrix", []),
        "review": values.get("review", {}),
        "artifacts": values.get("artifacts", {}),
        "decisions": values.get("decisions", []),
        "is_waiting_for_approval": is_waiting,
        "pending_checkpoint": interrupt_payload,
        "error": values.get("error"),
    }


@router.post("/{bid_id}/decisions")
@router.post("/{bid_id}/resume")
async def submit_bid_decision(bid_id: str, req: SubmitDecisionRequest) -> dict[str, Any]:
    """Resume an interrupted checkpoint with the human reviewer's decision."""
    config = {"configurable": {"thread_id": bid_id}}
    state_snapshot = bid_graph.get_state(config)

    if not state_snapshot or not state_snapshot.values:
        raise HTTPException(status_code=404, detail=f"Bid thread '{bid_id}' not found.")

    is_waiting = any(t.interrupts for t in state_snapshot.tasks) if state_snapshot.tasks else False
    if not is_waiting:
        raise HTTPException(
            status_code=400,
            detail=f"Bid '{bid_id}' is not currently waiting for a human decision.",
        )

    # Resume graph execution with Command(resume=...)
    command_input = Command(
        resume={
            "decision": req.decision,
            "comment": req.comment,
            "who": req.who,
        }
    )

    result = await bid_graph.ainvoke(command_input, config=config)

    new_snapshot = bid_graph.get_state(config)
    still_waiting = any(t.interrupts for t in new_snapshot.tasks) if new_snapshot.tasks else False

    return {
        "bid_id": bid_id,
        "status": result.get("status", "resumed"),
        "decision_submitted": req.decision,
        "outline_count": len(result.get("outline", [])),
        "outline": result.get("outline", []),
        "is_waiting_for_approval": still_waiting,
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

        state_snapshot = bid_graph.get_state(config)
        if state_snapshot and state_snapshot.values:
            yield {
                "event": "state_snapshot",
                "data": json.dumps({
                    "status": state_snapshot.values.get("status", "running"),
                    "requirements_count": len(state_snapshot.values.get("requirements", [])),
                }),
            }

        async for event in bid_graph.astream_events(None, config=config, version="v2"):
            kind = event.get("event")
            name = event.get("name", "")

            if kind == "on_chain_start" and name in (
                "ingest",
                "parse_documents",
                "extract_section_requirements",
                "finalize_requirements",
                "check_eligibility",
                "bid_decision",
                "plan_outline",
                "no_bid_summary",
            ):
                yield {
                    "event": "node_started",
                    "data": json.dumps({"node": name}),
                }
            elif kind == "on_chain_end" and name in (
                "ingest",
                "parse_documents",
                "extract_section_requirements",
                "finalize_requirements",
                "check_eligibility",
                "bid_decision",
                "plan_outline",
                "no_bid_summary",
            ):
                yield {
                    "event": "node_finished",
                    "data": json.dumps({"node": name}),
                }

        yield {
            "event": "completed",
            "data": json.dumps({"bid_id": bid_id, "status": "idle"}),
        }

    return EventSourceResponse(event_generator())


@router.get("/{bid_id}/download/{file_format}")
async def download_proposal_artifact(bid_id: str, file_format: str):
    """Download generated proposal DOCX or PDF artifact."""
    from fastapi.responses import FileResponse
    from pathlib import Path

    config = {"configurable": {"thread_id": bid_id}}
    state_snapshot = bid_graph.get_state(config)
    if not state_snapshot or not state_snapshot.values:
        raise HTTPException(status_code=404, detail=f"Bid thread '{bid_id}' not found.")

    artifacts = state_snapshot.values.get("artifacts", {})
    fmt = file_format.lower().strip()

    if fmt == "docx":
        file_path_str = artifacts.get("docx_path")
        media_type = "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    elif fmt == "pdf":
        file_path_str = artifacts.get("pdf_path")
        media_type = "application/pdf"
    else:
        raise HTTPException(status_code=400, detail="Invalid format. Supported: 'docx', 'pdf'.")

    if not file_path_str or not Path(file_path_str).exists():
        # Fallback check standard output directory
        alt_path = Path("output/documents") / f"Proposal_{bid_id}_{state_snapshot.values.get('bid', {}).get('tender_id', 'tender')}.{fmt}"
        if alt_path.exists():
            file_path_str = str(alt_path)
        else:
            raise HTTPException(status_code=404, detail=f"Artifact for format '{fmt}' not yet generated.")

    return FileResponse(
        path=file_path_str,
        media_type=media_type,
        filename=Path(file_path_str).name,
    )


class ExecuteTaskRequest(BaseModel):
    """Payload to request an on-demand copilot action or workspace task."""

    action: str = Field(
        description="Action type: 'qa', 'redraft_section', 'lookup_evidence', 'adjust_pricing', 'verify_compliance'"
    )
    params: dict[str, Any] = Field(
        default_factory=dict,
        description="Action-specific parameters (e.g. query, section_id, instructions, discount_pct)",
    )


@router.post("/{bid_id}/tasks")
@router.post("/{bid_id}/copilot")
async def execute_bid_task(bid_id: str, req: ExecuteTaskRequest) -> dict[str, Any]:
    """Execute an on-demand copilot action or workspace task."""
    from agent.app.agents.task_agent import task_agent

    result = await task_agent.execute(
        bid_id=bid_id,
        action=req.action,
        params=req.params,
    )
    if not result.get("success", False):
        raise HTTPException(
            status_code=400,
            detail=result.get("error", "Task execution failed"),
        )
    return result


