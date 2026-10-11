"""Unit tests for pricing MCP server."""

import sys
from pathlib import Path

import pytest

SERVER_DIR = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(SERVER_DIR))

from pricing_server import (
    build_price_sheet,
    estimate_effort,
    get_rate_card,
    mcp,
    pricing_assumptions_resource,
)


def test_get_rate_card_eur():
    card = get_rate_card("EUR")
    assert card["currency"] == "EUR"
    roles = card["roles"]
    assert "enterprise_architect" in roles
    assert roles["enterprise_architect"]["daily_rate"] == 1450.0
    assert roles["enterprise_architect"]["hourly_rate"] == 181.25


def test_get_rate_card_currencies():
    usd = get_rate_card("USD")
    assert usd["currency"] == "USD"
    assert usd["roles"]["lead_devops_engineer"]["daily_rate"] > 1000

    inr = get_rate_card("INR")
    assert inr["currency"] == "INR"
    assert inr["roles"]["senior_software_engineer"]["daily_rate"] > 70000


def test_estimate_effort():
    scope = [
        {
            "name": "AWS Landing Zone",
            "category": "architecture_design",
            "complexity": "medium",
            "quantity": 1.0,
        },
        {
            "name": "EKS Migration Wave 1",
            "category": "cloud_migration_service",
            "complexity": "high",
            "quantity": 1.0,
        },
    ]
    res = estimate_effort(scope)
    assert res["total_hours"] > 0
    assert len(res["items"]) == 2
    assert "lead_devops_engineer" in res["role_summary"]
    assert res["total_days"] == round(res["total_hours"] / 8.0, 2)


def test_build_price_sheet():
    lines = [
        {"role_key": "enterprise_architect", "hours": 40},
        {"role_key": "cloud_solutions_architect", "hours": 80},
        {"role_key": "lead_devops_engineer", "hours": 120},
    ]
    sheet = build_price_sheet(lines=lines, currency="EUR", margin=0.20)
    assert sheet["currency"] == "EUR"
    assert sheet["total_hours"] == 240
    assert sheet["subtotal_base_cost"] > 0
    assert sheet["total_margin"] == round(sheet["subtotal_base_cost"] * 0.20, 2)
    assert sheet["grand_total"] == round(sheet["subtotal_base_cost"] + sheet["total_margin"], 2)
    assert sheet["blended_hourly_rate"] > 0
    assert len(sheet["assumptions"]) >= 4


def test_pricing_assumptions_resource():
    res = pricing_assumptions_resource()
    assert "# Tychon Software Commercial Pricing Guidelines" in res
    assert "20% gross commercial margin" in res


@pytest.mark.asyncio
async def test_fastmcp_list_tools():
    tools = await mcp.list_tools()
    tool_names = [t.name for t in tools]
    assert "get_rate_card" in tool_names
    assert "estimate_effort" in tool_names
    assert "build_price_sheet" in tool_names
