"""Data models for pricing MCP server."""

from __future__ import annotations

from typing import Literal

from pydantic import BaseModel, Field


class ScopeItemInput(BaseModel):
    """Input definition for effort estimation."""

    name: str = Field(description="Name or title of the scope component (e.g. 'Landing Zone Setup')")
    category: str = Field(
        description="Category key (e.g. 'architecture_design', 'cloud_migration_service', 'devops_pipeline')"
    )
    complexity: Literal["low", "medium", "high"] = Field(
        default="medium", description="Complexity level"
    )
    quantity: float = Field(default=1.0, description="Multiplier / units of this scope item")
    description: str = Field(default="", description="Scope description or notes")


class RoleEffort(BaseModel):
    """Effort allocation for a specific role."""

    role_key: str
    role_title: str
    hours: float
    days: float


class ScopeEffortResult(BaseModel):
    """Calculated effort for an individual scope item."""

    item_name: str
    category: str
    complexity: str
    multiplier: float
    role_breakdown: list[RoleEffort]
    item_total_hours: float
    item_total_days: float


class EffortEstimateResponse(BaseModel):
    """Aggregated effort estimation across all scope items."""

    items: list[ScopeEffortResult]
    total_hours: float
    total_days: float
    role_summary: dict[str, float]  # role_key -> total hours


class PriceLineItem(BaseModel):
    """Pricing line item breakdown."""

    role_key: str
    role_title: str
    hours: float
    days: float
    hourly_rate: float
    daily_rate: float
    base_cost: float
    margin_amount: float
    line_total: float


class PriceSheetResponse(BaseModel):
    """Full commercial price sheet with margin, currency, and assumptions."""

    currency: str
    margin_percentage: float
    lines: list[PriceLineItem]
    total_hours: float
    total_days: float
    subtotal_base_cost: float
    total_margin: float
    grand_total: float
    blended_hourly_rate: float
    blended_daily_rate: float
    assumptions: list[str]
