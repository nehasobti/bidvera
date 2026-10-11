"""Unit tests for tender-search MCP server."""

import sys
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVER_DIR))

from tender_search_server import (
    get_document,
    get_tender,
    list_documents,
    load_registry,
    mcp,
    search_tenders,
    tender_summary_resource,
)


def test_registry_loading():
    items = load_registry()
    assert len(items) >= 3
    ids = [item.id for item in items]
    assert "tender-001" in ids
    assert "tender-002" in ids
    assert "tender-003" in ids


def test_search_tenders_all():
    results = search_tenders()
    assert len(results) >= 3


def test_search_tenders_query_filter():
    results = search_tenders(query="cloud")
    assert len(results) >= 1
    assert any("tender-001" == r["id"] for r in results)


def test_search_tenders_country_filter():
    results = search_tenders(country="India")
    assert len(results) >= 1
    assert all(r["country"] == "India" for r in results)


def test_search_tenders_category_filter():
    results = search_tenders(category="Data & AI")
    assert len(results) >= 1
    assert any("tender-002" == r["id"] for r in results)


def test_search_tenders_deadline_filter():
    results = search_tenders(deadline_after="2026-12-01T00:00:00Z")
    assert len(results) == 1
    assert results[0]["id"] == "tender-002"


def test_get_tender():
    t1 = get_tender("tender-001")
    assert t1["id"] == "tender-001"
    assert "EuroRailways" in t1["buyer"]
    assert len(t1["documents"]) >= 2
    assert len(t1["eligibility_criteria"]) >= 4

    missing = get_tender("tender-999")
    assert "error" in missing


def test_list_documents():
    docs = list_documents("tender-001")
    assert len(docs) >= 2
    doc_ids = [d["id"] for d in docs]
    assert "doc-001-main" in doc_ids


def test_get_document():
    doc = get_document("tender-001", "doc-001-main")
    assert "error" not in doc
    assert doc["tender_id"] == "tender-001"
    assert doc["doc_id"] == "doc-001-main"
    assert "Cloud Migration" in doc["text_content"]
    assert doc["sections_count"] > 0
    assert doc["tables_count"] > 0


def test_tender_summary_resource():
    summary = tender_summary_resource("tender-001")
    assert "# Cloud Migration & Hybrid DevOps Infrastructure" in summary
    assert "EuroRailways Digital" in summary


@pytest.mark.asyncio
async def test_fastmcp_list_tools():
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "search_tenders" in tool_names
    assert "get_tender" in tool_names
    assert "list_documents" in tool_names
    assert "get_document" in tool_names
