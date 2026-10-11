"""Tests for core LangGraph workflow: ingest, parse, parallel requirement extraction, and eligibility."""

import pytest
from langgraph.checkpoint.memory import MemorySaver

from agent.app.graph.main_graph import create_bid_graph


@pytest.mark.asyncio
async def test_bid_graph_execution_tender_001():
    # Use isolated MemorySaver checkpointer for test
    checkpointer = MemorySaver()
    graph = create_bid_graph(checkpointer=checkpointer)

    thread_id = "test-bid-001"
    initial_state = {
        "bid": {
            "id": thread_id,
            "tender_id": "tender-001",
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

    config = {"configurable": {"thread_id": thread_id}}
    result = await graph.ainvoke(initial_state, config=config)

    # 1. Verify Ingest & Parse
    assert result["status"] == "eligibility_checked"
    assert "EuroRailways" in result["bid"]["buyer"]
    assert len(result["documents"]) >= 2

    # 2. Verify Parallel Requirement Extraction
    requirements = result["requirements"]
    assert len(requirements) >= 3
    req_ids = [r["id"] for r in requirements]
    assert any("REQ-001" in rid or "REQ" in rid for rid in req_ids)

    # 3. Verify Eligibility Result
    eligibility = result["eligibility"]
    assert eligibility["recommendation"] == "bid"
    assert len(eligibility["reasons"]) > 0
    criteria_results = eligibility["criteria_results"]
    assert len(criteria_results) >= 3
    assert all(c["status"] == "met" for c in criteria_results)

    # 4. Verify Checkpointer Persistence
    saved_state = graph.get_state(config)
    assert saved_state is not None
    assert saved_state.values["bid"]["id"] == thread_id
    assert saved_state.values["status"] == "eligibility_checked"
