"""Unit and workflow tests for Phase 4: Content Generation and Pricing Engine."""

import pytest
from langgraph.types import Command
from agent.app.graph.main_graph import create_bid_graph
from langgraph.checkpoint.memory import MemorySaver


@pytest.mark.asyncio
async def test_section_drafting_and_pricing_pipeline():
    """Verify that approving a bid runs outline planning, parallel section drafting, and commercial pricing."""
    checkpointer = MemorySaver()
    graph = create_bid_graph(checkpointer=checkpointer)

    thread_id = "test-phase4-bid"
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

    # 1. Run up to bid_decision interrupt checkpoint
    result = await graph.ainvoke(initial_state, config=config)
    assert result["status"] == "eligibility_checked"

    snapshot = graph.get_state(config)
    assert len(snapshot.tasks) > 0
    assert len(snapshot.tasks[0].interrupts) > 0

    # 2. Human reviewer approves the bid
    resume_command = Command(
        resume={
            "decision": "bid",
            "comment": "Strategic priority approved for full section generation and pricing.",
            "who": "Chief Commercial Officer",
        }
    )

    final_result = await graph.ainvoke(resume_command, config=config)

    # 3. Verify proposal outline was generated
    outline = final_result.get("outline", [])
    assert len(outline) >= 5, f"Expected at least 5 outline sections, got {len(outline)}"

    # 4. Verify all sections were drafted in parallel
    sections = final_result.get("sections", [])
    assert len(sections) >= 5, f"Expected at least 5 drafted sections, got {len(sections)}"
    for sec in sections:
        assert "title" in sec
        assert "content" in sec
        assert len(sec["content"]) > 50, f"Section {sec.get('title')} content is too short"
        assert sec.get("word_count", 0) > 10

    # 5. Verify commercial pricing and effort breakdown
    pricing = final_result.get("pricing", {})
    assert "total_price" in pricing
    assert pricing["total_price"] > 0
    assert "effort" in pricing
    assert pricing["effort"].get("total_hours", 0) > 0

    price_sheet = pricing.get("price_sheet", {})
    assert "line_items" in price_sheet
    assert len(price_sheet["line_items"]) > 0
