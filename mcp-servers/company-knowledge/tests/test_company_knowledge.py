"""Unit tests for company-knowledge MCP server."""

import sys
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVER_DIR))

from company_knowledge_server import (
    company_profile_resource,
    company_voice,
    find_case_studies,
    get_cv,
    get_profile,
    list_certifications,
    mcp,
    search_knowledge,
)


def test_get_profile():
    p = get_profile()
    assert "error" not in p
    assert p["legal_name"] == "Tychon Software Solutions Private Limited"
    assert p["years_in_business"] >= 10
    assert p["financials"]["turnover"][0]["turnover_eur"] > 15000000


def test_list_certifications():
    certs = list_certifications()
    assert len(certs) >= 4
    iso27001 = next((c for c in certs if c["id"] == "CERT-ISO-27001"), None)
    assert iso27001 is not None
    assert iso27001["is_valid"] is True

    oracle = next((c for c in certs if c["id"] == "CERT-ORACLE-GOLD"), None)
    assert oracle is not None
    assert oracle["is_valid"] is False


def test_find_case_studies_tags():
    studies = find_case_studies(tags=["aws"])
    assert len(studies) >= 1
    assert any(s["id"] == "CS-001" for s in studies)


def test_find_case_studies_industry():
    studies = find_case_studies(industry="Healthcare")
    assert len(studies) >= 1
    assert studies[0]["id"] == "CS-002"


def test_get_cv_role():
    cvs = get_cv(role="Cloud Architect")
    assert len(cvs) >= 1
    assert "Anshuman Verma" in cvs[0]["name"]


def test_get_cv_skills():
    cvs = get_cv(skills=["Terraform"])
    assert len(cvs) >= 1
    names = [c["name"] for c in cvs]
    assert any("Priya Sharma" in n or "Anshuman Verma" in n for n in names)


def test_search_knowledge_hybrid():
    results = search_knowledge(query="cloud migration zero downtime", top_k=3)
    assert len(results) > 0
    assert any("chk-cs-CS-001" in r["chunk_id"] or "chk-prop-PROP-001" in r["chunk_id"] for r in results)


def test_resources_and_prompts():
    prof_md = company_profile_resource()
    assert "# Tychon Software" in prof_md

    voice_prompt = company_voice()
    assert "Tychon Software" in voice_prompt
    assert "[NEEDS INPUT:" in voice_prompt


@pytest.mark.asyncio
async def test_fastmcp_list_tools():
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "get_profile" in tool_names
    assert "search_knowledge" in tool_names
    assert "find_case_studies" in tool_names
    assert "list_certifications" in tool_names
    assert "get_cv" in tool_names
