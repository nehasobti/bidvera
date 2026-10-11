"""Tests for on-demand TaskAgent and copilot actions."""

import pytest
from starlette.testclient import TestClient
from agent.app.main import app

client = TestClient(app)


def test_copilot_task_actions():
    # 1. Start a bid to establish state
    res_start = client.post("/bids", json={"tender_id": "tender-001"})
    assert res_start.status_code == 201
    bid_id = res_start.json()["bid_id"]

    # 2. Test Tender Q&A task
    res_qa = client.post(
        f"/bids/{bid_id}/tasks",
        json={"action": "qa", "params": {"query": "What is the availability SLA?"}},
    )
    assert res_qa.status_code == 200
    qa_data = res_qa.json()
    assert qa_data["success"] is True
    assert "99.95%" in qa_data["answer"]
    assert len(qa_data["citations"]) > 0

    # 3. Test evidence lookup task
    res_lookup = client.post(
        f"/bids/{bid_id}/tasks",
        json={"action": "lookup_evidence", "params": {"category": "certifications"}},
    )
    assert res_lookup.status_code == 200
    lookup_data = res_lookup.json()
    assert lookup_data["success"] is True

    # 4. Test pricing scenario discount task
    res_pricing = client.post(
        f"/bids/{bid_id}/tasks",
        json={"action": "adjust_pricing", "params": {"discount_pct": 10.0}},
    )
    assert res_pricing.status_code == 200
    pricing_data = res_pricing.json()
    assert pricing_data["success"] is True
    assert pricing_data["discount_pct"] == 10.0
    assert pricing_data["scenario_price"] < pricing_data["original_price"]

    # 5. Test compliance verification task
    res_comp = client.post(
        f"/bids/{bid_id}/tasks",
        json={
            "action": "verify_compliance",
            "params": {
                "requirement_text": "Must have ISO 27001 accreditation and AWS partner status",
                "section_content": "Tychon Software maintains active ISO 27001 accreditation and is an AWS Premier partner.",
            },
        },
    )
    assert res_comp.status_code == 200
    comp_data = res_comp.json()
    assert comp_data["success"] is True
    assert comp_data["status"] == "Compliant"
