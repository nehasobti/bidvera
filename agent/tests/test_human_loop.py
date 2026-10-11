"""Tests for Phase 3 human-in-the-loop interrupts: bid/no-bid decision and outline planning."""

import pytest
from langgraph.checkpoint.memory import MemorySaver
from langgraph.types import Command
from starlette.testclient import TestClient

from agent.app.api.main import app
from agent.app.graph.main_graph import create_bid_graph

client = TestClient(app)


@pytest.mark.asyncio
async def test_bid_decision_interrupt_and_bid_path():
    checkpointer = MemorySaver()
    graph = create_bid_graph(checkpointer=checkpointer)
    thread_id = "test-hil-bid-01"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "bid": {"id": thread_id, "tender_id": "tender-001", "status": "created"},
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

    # Step 1: Run graph up to interrupt
    result = await graph.ainvoke(initial_state, config=config)
    assert "__interrupt__" in result
    interrupts = result["__interrupt__"]
    assert len(interrupts) > 0
    assert interrupts[0].value["type"] == "bid_decision"
    assert interrupts[0].value["recommendation"] == "bid"

    # Verify state snapshot reports pending task
    snapshot = graph.get_state(config)
    assert len(snapshot.tasks) > 0
    assert snapshot.tasks[0].name == "bid_decision"

    # Step 2: Resume with "bid" decision
    resume_cmd = Command(resume={"decision": "bid", "comment": "Strategic fit for cloud team", "who": "manager"})
    final_result = await graph.ainvoke(resume_cmd, config=config)

    assert final_result["status"] == "outline_planned"
    assert len(final_result["outline"]) == 6
    assert len(final_result["decisions"]) == 1
    assert final_result["decisions"][0]["decision"] == "bid"


@pytest.mark.asyncio
async def test_bid_decision_interrupt_and_no_bid_path():
    checkpointer = MemorySaver()
    graph = create_bid_graph(checkpointer=checkpointer)
    thread_id = "test-hil-nobid-02"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "bid": {"id": thread_id, "tender_id": "tender-002", "status": "created"},
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

    # Run up to interrupt
    await graph.ainvoke(initial_state, config=config)

    # Resume with "no-bid" decision
    resume_cmd = Command(resume={"decision": "no-bid", "comment": "Resource capacity constraints", "who": "manager"})
    final_result = await graph.ainvoke(resume_cmd, config=config)

    assert final_result["status"] == "no_bid_concluded"
    assert "no_bid_summary" in final_result["review"]
    assert len(final_result["decisions"]) == 1
    assert final_result["decisions"][0]["decision"] == "no-bid"


def test_api_approvals_inbox_and_decision_endpoint():
    # 1. Start a bid via API
    res_start = client.post("/bids", json={"tender_id": "tender-001"})
    assert res_start.status_code == 201
    data = res_start.json()
    bid_id = data["bid_id"]
    assert data["is_waiting_for_approval"] is True

    # 2. Check approvals inbox
    res_inbox = client.get("/bids/approvals/inbox")
    assert res_inbox.status_code == 200
    inbox = res_inbox.json()
    assert any(item["bid_id"] == bid_id for item in inbox)

    # 3. Submit decision via API
    res_decide = client.post(
        f"/bids/{bid_id}/decisions",
        json={"decision": "bid", "comment": "Approved by board", "who": "alex_manager"},
    )
    assert res_decide.status_code == 200
    decide_data = res_decide.json()
    assert decide_data["decision_submitted"] == "bid"
    assert decide_data["outline_count"] == 6
    assert decide_data["is_waiting_for_approval"] is False
