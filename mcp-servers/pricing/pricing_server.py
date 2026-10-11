"""Pricing MCP Server.

Provides tools for retrieving standard rate cards, estimating effort based on scope rules,
and assembling commercial price sheets with margin and assumption modeling.
"""

from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Any

import uvicorn
import yaml
from mcp.server.fastmcp import FastMCP
from pricing_models import (
    EffortEstimateResponse,
    PriceLineItem,
    PriceSheetResponse,
    RoleEffort,
    ScopeEffortResult,
    ScopeItemInput,
)
from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import JSONResponse, Response

SERVER_NAME = "pricing"
SERVER_VERSION = "0.1.0"


def get_data_dir() -> Path:
    env_dir = os.environ.get("COMPANY_DATA_DIR")
    if env_dir and Path(env_dir).exists():
        return Path(env_dir)
    candidates = [
        Path.cwd() / "sample-data" / "company",
        Path(__file__).resolve().parent.parent.parent / "sample-data" / "company",
        Path(__file__).resolve().parent / "data",
    ]
    for c in candidates:
        if c.exists():
            return c
    return candidates[0]


def load_rate_card() -> dict[str, Any]:
    rc_file = get_data_dir() / "rate_card.yaml"
    if not rc_file.exists():
        return {}
    with open(rc_file, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


def load_effort_rules() -> dict[str, Any]:
    rules_file = get_data_dir() / "effort_rules.yaml"
    if not rules_file.exists():
        return {}
    with open(rules_file, encoding="utf-8") as f:
        return yaml.safe_load(f) or {}


mcp = FastMCP(
    name=SERVER_NAME,
    instructions="MCP Server for commercial rate card access, rule-based effort estimation, and price sheets."
)


@mcp.tool()
def get_rate_card(currency: str = "EUR") -> dict[str, Any]:
    """Retrieve official company rate card by role in specified currency (EUR, USD, INR).

    Args:
        currency: ISO-4217 currency code (default 'EUR'). Supported: EUR, USD, INR.

    Returns:
        Role definitions with hourly and daily billing rates.
    """
    card = load_rate_card()
    if not card:
        return {"error": "Rate card configuration not found."}

    curr = currency.upper().strip()
    rate_multiplier = card.get("exchange_rates", {}).get(curr, 1.0)
    roles = card.get("roles", {})

    processed_roles: dict[str, Any] = {}
    for role_key, r_info in roles.items():
        daily_key = f"daily_rate_{curr.lower()}"
        hourly_key = f"hourly_rate_{curr.lower()}"

        daily = r_info.get(daily_key) or round(r_info.get("daily_rate_eur", 1000.0) * rate_multiplier, 2)
        hourly = r_info.get(hourly_key) or round(daily / 8.0, 2)

        processed_roles[role_key] = {
            "title": r_info["title"],
            "seniority": r_info["seniority"],
            "currency": curr,
            "daily_rate": daily,
            "hourly_rate": hourly,
        }

    return {
        "currency": curr,
        "effective_date": card.get("effective_date", "2026-01-01"),
        "valid_until": card.get("valid_until", "2026-12-31"),
        "roles": processed_roles,
    }


@mcp.tool()
def estimate_effort(scope_items: list[dict[str, Any]]) -> dict[str, Any]:
    """Estimate effort in person-hours and person-days based on scope items and complexity rules.

    Args:
        scope_items: List of scope item dicts, each having:
          - name: str (e.g. 'Landing Zone Provisioning')
          - category: str (e.g. 'architecture_design', 'cloud_migration_service', 'devops_pipeline')
          - complexity: 'low', 'medium', or 'high'
          - quantity: float (optional multiplier, default 1.0)

    Returns:
        Structured breakdown of hours per role and total project effort.
    """
    rules = load_effort_rules()
    rate_card = load_rate_card()
    roles_def = rate_card.get("roles", {})

    multipliers = rules.get("complexity_multipliers", {"low": 0.7, "medium": 1.0, "high": 1.6})
    baselines = rules.get("category_baseline_hours", {})

    items_result: list[ScopeEffortResult] = []
    role_summary: dict[str, float] = {}
    grand_total_hours = 0.0

    for raw_item in scope_items:
        inp = ScopeItemInput(**raw_item)
        cat_rule = baselines.get(inp.category, baselines.get("cloud_migration_service", {}))
        cat_roles = cat_rule.get("roles", {"senior_software_engineer": 40})
        mult = multipliers.get(inp.complexity, 1.0) * inp.quantity

        role_breakdown: list[RoleEffort] = []
        item_hours = 0.0

        for r_key, base_h in cat_roles.items():
            h = round(base_h * mult, 1)
            d = round(h / 8.0, 2)
            title = roles_def.get(r_key, {}).get("title", r_key.replace("_", " ").title())
            role_breakdown.append(RoleEffort(role_key=r_key, role_title=title, hours=h, days=d))
            item_hours += h

            role_summary[r_key] = round(role_summary.get(r_key, 0.0) + h, 1)

        grand_total_hours += item_hours
        items_result.append(
            ScopeEffortResult(
                item_name=inp.name,
                category=inp.category,
                complexity=inp.complexity,
                multiplier=round(mult, 2),
                role_breakdown=role_breakdown,
                item_total_hours=round(item_hours, 1),
                item_total_days=round(item_hours / 8.0, 2),
            )
        )

    res = EffortEstimateResponse(
        items=items_result,
        total_hours=round(grand_total_hours, 1),
        total_days=round(grand_total_hours / 8.0, 2),
        role_summary=role_summary,
    )
    return res.model_dump()


@mcp.tool()
def build_price_sheet(
    lines: list[dict[str, Any]],
    currency: str = "EUR",
    margin: float = 0.20,
) -> dict[str, Any]:
    """Calculate commercial price sheet applying rate card pricing, target gross margin, and standard assumptions.

    Args:
        lines: List of effort lines, each containing either:
          - role_key: str and hours: float, OR
          - role_key: str and days: float
        currency: ISO currency code ('EUR', 'USD', 'INR').
        margin: Target gross margin fraction (e.g. 0.20 for 20%).

    Returns:
        Detailed commercial price sheet with base cost, margin, grand total, and blended rates.
    """
    card = get_rate_card(currency)
    curr = card.get("currency", "EUR")
    roles = card.get("roles", {})

    price_lines: list[PriceLineItem] = []
    subtotal_base_cost = 0.0
    total_hours = 0.0

    for line in lines:
        r_key = line.get("role_key", "senior_software_engineer")
        r_info = roles.get(r_key, roles.get("senior_software_engineer", {}))

        h = float(line.get("hours", 0.0))
        if h == 0.0 and "days" in line:
            h = float(line["days"]) * 8.0
        d = round(h / 8.0, 2)

        hourly_rate = float(r_info.get("hourly_rate", 100.0))
        daily_rate = float(r_info.get("daily_rate", 800.0))

        base_cost = round(h * hourly_rate, 2)
        margin_amt = round(base_cost * margin, 2)
        line_total = round(base_cost + margin_amt, 2)

        subtotal_base_cost += base_cost
        total_hours += h

        price_lines.append(
            PriceLineItem(
                role_key=r_key,
                role_title=r_info.get("title", r_key),
                hours=round(h, 1),
                days=d,
                hourly_rate=hourly_rate,
                daily_rate=daily_rate,
                base_cost=base_cost,
                margin_amount=margin_amt,
                line_total=line_total,
            )
        )

    total_margin = round(subtotal_base_cost * margin, 2)
    grand_total = round(subtotal_base_cost + total_margin, 2)
    blended_h = round(grand_total / total_hours, 2) if total_hours > 0 else 0.0
    blended_d = round(blended_h * 8.0, 2)

    assumptions = [
        "1. Standard working day comprises 8 working hours, Monday to Friday.",
        "2. All rates are exclusive of Value Added Tax (VAT) or statutory local sales taxes.",
        f"3. Firm fixed pricing quoted in {curr}, valid for 90 calendar days from quotation.",
        "4. Travel and lodging outside designated hubs billed at actuals upon client pre-approval.",
        "5. Overtime or weekend deployments require 1.5x surge rate agreement.",
    ]

    res = PriceSheetResponse(
        currency=curr,
        margin_percentage=margin,
        lines=price_lines,
        total_hours=round(total_hours, 1),
        total_days=round(total_hours / 8.0, 2),
        subtotal_base_cost=round(subtotal_base_cost, 2),
        total_margin=total_margin,
        grand_total=grand_total,
        blended_hourly_rate=blended_h,
        blended_daily_rate=blended_d,
        assumptions=assumptions,
    )
    return res.model_dump()


@mcp.resource("pricing://assumptions")
def pricing_assumptions_resource() -> str:
    """Standard commercial pricing assumptions and rate-card guidelines."""
    return (
        "# Tychon Software Commercial Pricing Guidelines\n\n"
        "### Key Principles\n"
        "- **Base Currency:** EUR (€), with parity conversion for USD ($) and INR (₹).\n"
        "- **Standard Margin Target:** 20% gross commercial margin.\n"
        "- **Blended Delivery Model:** Dual EU/Munich & India/Bengaluru delivery center structure.\n\n"
        "### Terms & Conditions\n"
        "1. Invoicing on milestone delivery with net-30 payment terms.\n"
        "2. 90-day post-go-live warranty included in fixed-price quotes.\n"
        "3. Rate card holds firm through December 31, 2026.\n"
    )


class BearerAuthMiddleware(BaseHTTPMiddleware):
    """Enforces Bearer token auth for MCP endpoints when MCP_AUTH_TOKEN is configured."""

    async def dispatch(self, request: Request, call_next: Any) -> Response:
        if request.url.path in ("/health", "/"):
            return await call_next(request)

        expected_token = os.environ.get("MCP_AUTH_TOKEN") or os.environ.get("PRICING_AUTH_TOKEN")
        if expected_token:
            auth_header = request.headers.get("Authorization", "")
            if not auth_header.startswith("Bearer ") or auth_header[7:].strip() != expected_token:
                return JSONResponse(
                    {"error": "Unauthorized: Invalid or missing Bearer token"},
                    status_code=401,
                )

        return await call_next(request)


def create_asgi_app() -> Any:
    """Builds ASGI Starlette app with middleware and health endpoint."""
    app = mcp.sse_app()
    app.add_middleware(BearerAuthMiddleware)

    async def health_endpoint(_: Request) -> JSONResponse:
        card = load_rate_card()
        return JSONResponse(
            {
                "status": "healthy",
                "server": SERVER_NAME,
                "version": SERVER_VERSION,
                "roles_count": len(card.get("roles", {})),
            }
        )

    app.add_route("/health", health_endpoint, methods=["GET"])
    return app


def main() -> None:
    parser = argparse.ArgumentParser(description=f"{SERVER_NAME} MCP Server")
    parser.add_argument("--transport", choices=["stdio", "sse", "http"], default="sse")
    parser.add_argument("--host", default=os.environ.get("MCP_HOST", "0.0.0.0"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("PORT", "8003")))
    args = parser.parse_args()

    if args.transport == "stdio":
        mcp.run(transport="stdio")
    else:
        app = create_asgi_app()
        uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
