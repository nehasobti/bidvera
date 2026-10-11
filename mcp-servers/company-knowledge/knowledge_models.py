"""Data models for company-knowledge MCP server."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class CompanyProfile(BaseModel):
    """Corporate profile and baseline company facts."""

    company_id: str
    legal_name: str
    trade_name: str
    eu_entity: str
    founded_year: int
    years_in_business: int
    headquarters: dict[str, Any]
    duns_number: str
    financials: dict[str, Any]
    workforce: dict[str, Any]
    core_competencies: list[str]
    partnerships: list[dict[str, Any]]
    overview: str


class CertificationItem(BaseModel):
    """Certification record with validity and verification details."""

    id: str
    name: str
    issuing_body: str
    certificate_number: str
    issue_date: str
    expiry_date: str
    status: str
    scope: str
    verification_url: str
    is_valid: bool = True


class CaseStudyItem(BaseModel):
    """Past project delivery case study with metrics."""

    id: str
    title: str
    client: str
    industry: str
    country: str
    year: int
    duration_months: int
    budget_eur: float
    tags: list[str]
    challenge: str
    solution: str
    metrics: dict[str, Any]
    outcomes: str
    technologies: list[str]


class StaffCV(BaseModel):
    """Expert CV profile."""

    id: str
    name: str
    role: str
    years_of_experience: int
    location: str
    education: str
    certifications: list[str]
    skills: list[str]
    bio: str
    selected_projects: list[dict[str, Any]]


class KnowledgeChunk(BaseModel):
    """Searchable chunk for hybrid retrieval."""

    chunk_id: str
    doc_type: str  # proposal, case_study, certification, cv, policy
    source_id: str
    title: str
    text: str
    date: str
    score: float = 0.0
    metadata: dict[str, Any] = Field(default_factory=dict)
