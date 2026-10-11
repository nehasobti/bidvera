"""Unit tests for documents MCP server."""

import sys
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVER_DIR))

from documents_server import (
    add_compliance_matrix,
    convert_to_pdf,
    create_response_doc,
    final_checklist,
    get_download_url,
    mcp,
)


@pytest.fixture
def sample_bid_payload():
    return {
        "bid_id": "bid-test-001",
        "tender_id": "tender-001",
        "title": "Cloud Migration Proposal for EuroRailways Digital",
        "buyer": "EuroRailways Digital GmbH",
        "submission_date": "2026-11-15",
        "company_name": "Tychon Software GmbH",
        "executive_summary": "Tychon Software presents our technical approach for AWS cloud migration.",
        "sections": [
            {
                "title": "Architecture & Landing Zone",
                "content": "We propose a multi-account AWS landing zone with automated Transit Gateway and Terraform.",
                "citations": ["CS-001", "CERT-AWS-PREMIER"],
            },
            {
                "title": "DevOps & EKS Migration",
                "content": "Workloads are migrated in 4 distinct waves with ArgoCD GitOps pipelines on Amazon EKS.",
                "citations": ["CS-001", "CV-002"],
            },
        ],
        "pricing_summary": {
            "currency": "EUR",
            "total_hours": 320,
            "total_days": 40,
            "grand_total": 48500.0,
            "lines": [
                {
                    "role_title": "Enterprise / Chief Cloud Architect",
                    "days": 10,
                    "daily_rate": 1450.0,
                    "hours": 80,
                    "line_total": 14500.0,
                },
                {
                    "role_title": "Lead DevOps / Platform Engineer",
                    "days": 30,
                    "daily_rate": 980.0,
                    "hours": 240,
                    "line_total": 29400.0,
                },
            ],
        },
        "compliance_matrix": [
            {
                "req_id": "REQ-001",
                "description": "€10M annual turnover requirement",
                "type": "Mandatory",
                "compliance_status": "Compliant",
                "response_section": "Section 1",
                "evidence_citation": "profile.financials",
            },
            {
                "req_id": "REQ-002",
                "description": "Active ISO 27001 accreditation",
                "type": "Mandatory",
                "compliance_status": "Compliant",
                "response_section": "Section 2",
                "evidence_citation": "CERT-ISO-27001",
            },
        ],
    }


def test_create_response_doc(sample_bid_payload):
    res = create_response_doc(sample_bid_payload)
    assert "error" not in res
    assert "doc_id" in res
    assert res["bid_id"] == "bid-test-001"
    assert Path(res["docx_path"]).exists()
    assert res["docx_size_bytes"] > 0


def test_add_compliance_matrix(sample_bid_payload):
    doc_res = create_response_doc(sample_bid_payload)
    doc_id = doc_res["doc_id"]

    matrix_update = [
        {
            "req_id": "REQ-003",
            "description": "Zero unplanned downtime during migration",
            "type": "Mandatory",
            "compliance_status": "Compliant",
            "response_section": "Section 3",
            "evidence_citation": "CS-001",
        }
    ]
    res = add_compliance_matrix(doc_id=doc_id, matrix=matrix_update)
    assert "error" not in res
    assert res["status"] == "compliance_matrix_appended"
    assert res["matrix_entries_count"] == 1


def test_convert_to_pdf(sample_bid_payload):
    doc_res = create_response_doc(sample_bid_payload)
    doc_id = doc_res["doc_id"]

    pdf_res = convert_to_pdf(doc_id)
    assert "error" not in pdf_res
    assert Path(pdf_res["pdf_path"]).exists()
    assert pdf_res["pdf_size_bytes"] > 0
    assert pdf_res["converter_engine"] in ("libreoffice", "fpdf2_fallback")


def test_get_download_url(sample_bid_payload):
    doc_res = create_response_doc(sample_bid_payload)
    doc_id = doc_res["doc_id"]
    convert_to_pdf(doc_id)

    info = get_download_url(doc_id)
    assert info["docx_exists"] is True
    assert info["pdf_exists"] is True
    assert info["docx_size_bytes"] > 0
    assert info["pdf_size_bytes"] > 0


def test_final_checklist_prompt():
    prompt_text = final_checklist()
    assert "Final Proposal Quality & Verification Checklist" in prompt_text
    assert "Mandatory Compliance" in prompt_text


@pytest.mark.asyncio
async def test_fastmcp_list_tools():
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "create_response_doc" in tool_names
    assert "add_compliance_matrix" in tool_names
    assert "convert_to_pdf" in tool_names
    assert "get_download_url" in tool_names
