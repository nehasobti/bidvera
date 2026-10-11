"""Tests verifying checkpoint persistence and thread resumption."""

import pytest
from langgraph.checkpoint.memory import MemorySaver

from agent.app.graph.main_graph import create_bid_graph


@pytest.mark.asyncio
async def test_checkpoint_resume_across_instances():
    # Shared checkpointer simulating persistent storage
    shared_checkpointer = MemorySaver()
    thread_id = "test-resume-thread-01"
    config = {"configurable": {"thread_id": thread_id}}

    # Instance 1: Run graph
    graph_instance_1 = create_bid_graph(checkpointer=shared_checkpointer)
    initial_state = {
        "bid": {
            "id": thread_id,
            "tender_id": "tender-002",
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

    result = await graph_instance_1.ainvoke(initial_state, config=config)
    assert result["status"] == "eligibility_checked"

    # Simulate killing service and initializing a brand-new Graph instance
    del graph_instance_1
    graph_instance_2 = create_bid_graph(checkpointer=shared_checkpointer)

    # Instance 2: Retrieve checkpoint state
    saved_snapshot = graph_instance_2.get_state(config)
    assert saved_snapshot is not None
    assert saved_snapshot.values["bid"]["id"] == thread_id
    assert saved_snapshot.values["status"] == "eligibility_checked"
    assert len(saved_snapshot.values["requirements"]) > 0

    # Resume/continue with new input without re-running from scratch
    updated_state = await graph_instance_2.ainvoke(None, config=config)
    assert updated_state["status"] == "eligibility_checked"


@pytest.mark.asyncio
async def test_persistent_disk_saver_reloads_from_disk(tmp_path):
    from agent.app.core.db import PersistentDiskSaver

    checkpoint_file = tmp_path / "checkpoints_test.pkl"
    saver_1 = PersistentDiskSaver(file_path=checkpoint_file)
    thread_id = "test-disk-thread-01"
    config = {"configurable": {"thread_id": thread_id}}

    graph_1 = create_bid_graph(checkpointer=saver_1)
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

    result = await graph_1.ainvoke(initial_state, config=config)
    assert result["status"] == "eligibility_checked"
    assert checkpoint_file.exists()

    # Re-instantiate saver pointing to same file path (simulating app restart)
    saver_2 = PersistentDiskSaver(file_path=checkpoint_file)
    graph_2 = create_bid_graph(checkpointer=saver_2)

    snapshot = graph_2.get_state(config)
    assert snapshot is not None
    assert snapshot.values["bid"]["id"] == thread_id
    assert snapshot.values["status"] == "eligibility_checked"
    assert len(snapshot.values["requirements"]) > 0

