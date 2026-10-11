"""End-to-End MCP client test suite for all four Bidvera MCP servers:

1. tender-search
2. company-knowledge
3. pricing
4. documents

Verifies that an MCP client lists and successfully executes every tool across all four servers.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE_DIR / "mcp-servers" / "tender-search"))
sys.path.insert(0, str(BASE_DIR / "mcp-servers" / "company-knowledge"))
sys.path.insert(0, str(BASE_DIR / "mcp-servers" / "pricing"))
sys.path.insert(0, str(BASE_DIR / "mcp-servers" / "documents"))

import company_knowledge_server as ck_mod
import documents_server as doc_mod
import pricing_server as pr_mod
import tender_search_server as ts_mod


def extract_tool_result(call_res: Any) -> Any:
    """Extracts raw Python payload or parsed JSON from FastMCP call_tool."""
    if isinstance(call_res, tuple) and len(call_res) >= 2:
        meta_dict = call_res[1]
        if isinstance(meta_dict, dict) and "result" in meta_dict:
            return meta_dict["result"]

    blocks = call_res[0] if isinstance(call_res, (tuple, list)) else [call_res]
    if isinstance(blocks, list) and len(blocks) > 1:
        items: list[Any] = []
        for b in blocks:
            try:
                items.append(json.loads(b.text))
            except Exception:
                items.append(b.text)
        return items
    elif isinstance(blocks, list) and len(blocks) == 1:
        try:
            return json.loads(blocks[0].text)
        except Exception:
            return blocks[0].text
    return call_res


# -------------------------------------------------------------
# 1. Tender Search Server Verification
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_mcp_client_tender_search():
    mcp = ts_mod.mcp

    # 1. List tools
    tools = await mcp.list_tools()
    tool_map = {t.name: t for t in tools}
    assert "search_tenders" in tool_map
    assert "get_tender" in tool_map
    assert "list_documents" in tool_map
    assert "get_document" in tool_map

    # 2. Call search_tenders
    res = await mcp.call_tool("search_tenders", {"query": "cloud"})
    tenders = extract_tool_result(res)
    assert len(tenders) >= 1
    t1_id = tenders[0]["id"]

    # 3. Call get_tender
    res_get = await mcp.call_tool("get_tender", {"tender_id": t1_id})
    t_data = extract_tool_result(res_get)
    assert t_data["id"] == t1_id

    # 4. Call list_documents
    res_docs = await mcp.call_tool("list_documents", {"tender_id": t1_id})
    docs = extract_tool_result(res_docs)
    assert len(docs) >= 1
    doc_id = docs[0]["id"]

    # 5. Call get_document
    res_doc_content = await mcp.call_tool("get_document", {"tender_id": t1_id, "doc_id": doc_id})
    doc_data = extract_tool_result(res_doc_content)
    assert "text_content" in doc_data
    assert len(doc_data["text_content"]) > 0


# -------------------------------------------------------------
# 2. Company Knowledge Server Verification
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_mcp_client_company_knowledge():
    mcp = ck_mod.mcp

    # 1. List tools
    tools = await mcp.list_tools()
    tool_map = {t.name: t for t in tools}
    assert "get_profile" in tool_map
    assert "search_knowledge" in tool_map
    assert "find_case_studies" in tool_map
    assert "list_certifications" in tool_map
    assert "get_cv" in tool_map

    # 2. Call get_profile
    res_prof = await mcp.call_tool("get_profile", {})
    prof = extract_tool_result(res_prof)
    assert prof["trade_name"] == "Tychon Software"
    assert prof["years_in_business"] >= 10

    # 3. Call search_knowledge
    res_know = await mcp.call_tool("search_knowledge", {"query": "Kubernetes migration", "top_k": 3})
    know = extract_tool_result(res_know)
    assert len(know) > 0

    # 4. Call find_case_studies
    res_cs = await mcp.call_tool("find_case_studies", {"tags": ["aws"]})
    cs = extract_tool_result(res_cs)
    assert len(cs) >= 1

    # 5. Call list_certifications
    res_certs = await mcp.call_tool("list_certifications", {})
    certs = extract_tool_result(res_certs)
    assert len(certs) >= 4
    assert any(c["id"] == "CERT-ISO-27001" and c["is_valid"] is True for c in certs)

    # 6. Call get_cv
    res_cv = await mcp.call_tool("get_cv", {"role": "Architect"})
    cv_list = extract_tool_result(res_cv)
    assert len(cv_list) >= 1


# -------------------------------------------------------------
# 3. Pricing Server Verification
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_mcp_client_pricing():
    mcp = pr_mod.mcp

    # 1. List tools
    tools = await mcp.list_tools()
    tool_map = {t.name: t for t in tools}
    assert "get_rate_card" in tool_map
    assert "estimate_effort" in tool_map
    assert "build_price_sheet" in tool_map

    # 2. Call get_rate_card
    res_card = await mcp.call_tool("get_rate_card", {"currency": "EUR"})
    card = extract_tool_result(res_card)
    assert "enterprise_architect" in card["roles"]

    # 3. Call estimate_effort
    scope_payload = [
        {"name": "Discovery and Architecture", "category": "architecture_design", "complexity": "medium"},
        {"name": "Cloud Migration Waves", "category": "cloud_migration_service", "complexity": "high"},
    ]
    res_effort = await mcp.call_tool("estimate_effort", {"scope_items": scope_payload})
    effort = extract_tool_result(res_effort)
    assert effort["total_hours"] > 0
    assert "role_summary" in effort

    # 4. Call build_price_sheet
    lines = [
        {"role_key": "enterprise_architect", "hours": 40},
        {"role_key": "lead_devops_engineer", "hours": 120},
    ]
    res_sheet = await mcp.call_tool("build_price_sheet", {"lines": lines, "currency": "EUR", "margin": 0.20})
    sheet = extract_tool_result(res_sheet)
    assert sheet["grand_total"] > sheet["subtotal_base_cost"]
    assert sheet["currency"] == "EUR"


# -------------------------------------------------------------
# 4. Documents Server Verification
# -------------------------------------------------------------
@pytest.mark.asyncio
async def test_mcp_client_documents():
    mcp = doc_mod.mcp

    # 1. List tools
    tools = await mcp.list_tools()
    tool_map = {t.name: t for t in tools}
    assert "create_response_doc" in tool_map
    assert "add_compliance_matrix" in tool_map
    assert "convert_to_pdf" in tool_map
    assert "get_download_url" in tool_map

    # 2. Call create_response_doc
    bid_payload = {
        "bid_id": "bid-e2e-001",
        "tender_id": "tender-001",
        "title": "Comprehensive E2E Proposal for EuroRailways",
        "buyer": "EuroRailways Digital GmbH",
        "submission_date": "2026-11-18",
        "company_name": "Tychon Software GmbH",
        "executive_summary": "E2E proposal response demonstrating automated document creation.",
        "sections": [
            {
                "title": "Enterprise Cloud Architecture",
                "content": "Full landing zone and Kubernetes architecture following CIS benchmarks.",
                "citations": ["CS-001", "CERT-ISO-27001"],
            }
        ],
        "pricing_summary": {
            "currency": "EUR",
            "total_hours": 160,
            "total_days": 20,
            "grand_total": 24500.0,
            "lines": [
                {
                    "role_title": "Enterprise / Chief Cloud Architect",
                    "days": 20,
                    "daily_rate": 1225.0,
                    "hours": 160,
                    "line_total": 24500.0,
                }
            ],
        },
        "compliance_matrix": [
            {
                "req_id": "REQ-001",
                "description": "EUR 10M annual turnover requirement",
                "type": "Mandatory",
                "compliance_status": "Compliant",
                "response_section": "Executive Summary",
            }
        ],
    }

    res_create = await mcp.call_tool("create_response_doc", {"bid_json": bid_payload})
    doc_res = extract_tool_result(res_create)
    assert "doc_id" in doc_res
    doc_id = doc_res["doc_id"]
    assert Path(doc_res["docx_path"]).exists()

    # 3. Call add_compliance_matrix
    more_matrix = [
        {
            "req_id": "REQ-002",
            "description": "ISO 27001 active certificate",
            "type": "Mandatory",
            "compliance_status": "Compliant",
            "response_section": "Section 2",
            "evidence_citation": "CERT-ISO-27001",
        }
    ]
    res_matrix = await mcp.call_tool("add_compliance_matrix", {"doc_id": doc_id, "matrix": more_matrix})
    matrix_res = extract_tool_result(res_matrix)
    assert matrix_res["status"] == "compliance_matrix_appended"

    # 4. Call convert_to_pdf
    res_pdf = await mcp.call_tool("convert_to_pdf", {"doc_id": doc_id})
    pdf_res = extract_tool_result(res_pdf)
    assert Path(pdf_res["pdf_path"]).exists()
    assert pdf_res["pdf_size_bytes"] > 0

    # 5. Call get_download_url
    res_url = await mcp.call_tool("get_download_url", {"doc_id": doc_id})
    info = extract_tool_result(res_url)
    assert info["docx_exists"] is True
    assert info["pdf_exists"] is True
