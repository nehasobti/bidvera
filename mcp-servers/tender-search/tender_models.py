"""Data models for tender-search MCP server."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class TenderDocumentInfo(BaseModel):
    """Metadata describing a document associated with a tender."""

    id: str = Field(description="Unique identifier of the document (e.g. doc-001-main)")
    name: str = Field(description="File name of the document")
    type: str = Field(description="Document role/type (e.g. main_rfp, security_annex, technical_specs)")
    pages: int = Field(default=1, description="Estimated page count")
    file_path: str = Field(default="", description="Path to document file on disk")


class TenderItem(BaseModel):
    """Detailed metadata and scope for a tender."""

    id: str = Field(description="Unique identifier of the tender (e.g. tender-001)")
    title: str = Field(description="Official tender title")
    buyer: str = Field(description="Procurement authority / buyer organization")
    country: str = Field(description="Country or economic area (e.g. EU, Germany, India)")
    category: str = Field(description="Tender category (e.g. Cloud Migration, Data & AI, Software Development)")
    deadline: str = Field(description="Submission deadline in ISO-8601 format")
    estimated_budget_eur: float | None = Field(default=None, description="Estimated budget in EUR")
    summary: str = Field(description="Executive summary of the procurement scope")
    documents: list[TenderDocumentInfo] = Field(default_factory=list, description="Associated document files")
    eligibility_criteria: list[dict[str, Any]] = Field(default_factory=list, description="Mandatory & scored criteria")


class TenderDocumentContent(BaseModel):
    """Extracted text and structural contents of a tender document."""

    tender_id: str = Field(description="ID of the parent tender")
    doc_id: str = Field(description="Unique document ID")
    name: str = Field(description="Document name")
    content_type: str = Field(description="MIME type or file extension")
    text_content: str = Field(description="Extracted textual content")
    sections_count: int = Field(default=0, description="Number of detected sections")
    tables_count: int = Field(default=0, description="Number of detected tables")
