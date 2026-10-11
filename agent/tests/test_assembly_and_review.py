"""Tests for Phase 5: Proposal Assembly, Review & Quality Control, and Artifact Generation."""

import pytest
from langgraph.types import Command
from agent.app.graph.main_graph import create_bid_graph
from langgraph.checkpoint.memory import MemorySaver


@pytest.mark.asyncio
async def test_full_proposal_assembly_and_review_pipeline():
    """Verify end-to-end pipeline: outline -> drafting -> pricing -> compliance matrix -> review -> docx & pdf."""
    checkpointer = MemorySaver()
    graph = create_bid_graph(checkpointer=checkpointer)

    thread_id = "test-phase5-full-pipeline"
    config = {"configurable": {"thread_id": thread_id}}

    initial_state = {
        "bid": {
            "id": thread_id,
            "tender_id": "tender-001",
            "title": "Cloud Migration & Hybrid DevOps Infrastructure",
            "buyer": "EuroRailways Digital GmbH",
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

    # 1. Run up to bid_decision checkpoint
    step1 = await graph.ainvoke(initial_state, config=config)
    assert step1["status"] == "eligibility_checked"

    # 2. Approve bid decision
    resume_cmd = Command(
        resume={
            "decision": "bid",
            "comment": "Approved for full proposal assembly and PDF delivery.",
            "who": "Commercial Director",
        }
    )
    final_result = await graph.ainvoke(resume_cmd, config=config)

    # 3. Verify compliance matrix
    matrix = final_result.get("compliance_matrix", [])
    assert len(matrix) >= 3, "Expected compliance matrix entries"
    for entry in matrix:
        assert "requirement_id" in entry
        assert "compliance_status" in entry
        assert entry["compliance_status"] == "Compliant"

    # 4. Verify review and QA scoring
    review = final_result.get("review", {})
    assert "score" in review
    assert review["score"] > 80.0
    assert review["status"] == "approved"
    assert review.get("requirement_coverage_pct", 0) > 80.0

    # 5. Verify DOCX and PDF document artifacts
    artifacts = final_result.get("artifacts", {})
    assert "docx_path" in artifacts
    assert "pdf_path" in artifacts
    assert artifacts["status"] == "ready"
    assert "docx_filename" in artifacts
    assert "pdf_filename" in artifacts
