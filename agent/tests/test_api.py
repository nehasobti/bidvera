"""Tests for FastAPI endpoints: start, status, stream, and resume."""

from starlette.testclient import TestClient

from agent.app.api.main import app

client = TestClient(app)


def test_health_endpoint():
    res = client.get("/health")
    assert res.status_code == 200
    data = res.json()
    assert data["status"] == "healthy"
    assert data["service"] == "agent-api"


def test_start_and_get_bid():
    # 1. Start a new bid
    payload = {"tender_id": "tender-001"}
    res = client.post("/bids", json=payload)
    assert res.status_code == 201
    start_data = res.json()
    assert "bid_id" in start_data
    bid_id = start_data["bid_id"]
    assert start_data["requirements_count"] >= 3
    assert start_data["eligibility_recommendation"] == "bid"

    # 2. Query bid state
    res_get = client.get(f"/bids/{bid_id}")
    assert res_get.status_code == 200
    get_data = res_get.json()
    assert get_data["bid_id"] == bid_id
    assert get_data["status"] == "eligibility_checked"
    assert len(get_data["requirements"]) >= 3
    assert get_data["eligibility"]["recommendation"] == "bid"


def test_resume_bid():
    # Start a bid
    res_start = client.post("/bids", json={"tender_id": "tender-003"})
    bid_id = res_start.json()["bid_id"]

    # Resume bid
    resume_payload = {
        "decision": "bid",
        "comment": "Proceed with bid response",
        "who": "bid_manager",
    }
    res_resume = client.post(f"/bids/{bid_id}/resume", json=resume_payload)
    assert res_resume.status_code == 200
    resume_data = res_resume.json()
    assert resume_data["bid_id"] == bid_id


def test_stream_bid():
    # Start bid
    res_start = client.post("/bids", json={"tender_id": "tender-001"})
    bid_id = res_start.json()["bid_id"]

    # Connect to stream
    with client.stream("GET", f"/bids/{bid_id}/stream") as response:
        assert response.status_code == 200
        # Read initial events
        lines = [line if isinstance(line, str) else line.decode("utf-8") for line in response.iter_lines()]
        joined = "".join(lines)
        assert "connected" in joined
