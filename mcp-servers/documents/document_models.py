"""Data models for documents MCP server."""

from __future__ import annotations

from typing import Any

from pydantic import BaseModel, Field


class BidDocumentInput(BaseModel):
    """Complete structured bid payload for document generation."""

    bid_id: str = Field(description="Unique bid thread ID")
    tender_id: str = Field(description="Target tender ID")
    title: str = Field(description="Official response proposal title")
    buyer: str = Field(description="Buyer authority name")
    submission_date: str = Field(default="", description="Proposal submission date")
    company_name: str = Field(default="Tychon Software", description="Submitting bidder name")
    executive_summary: str = Field(default="", description="Executive summary section text")
    sections: list[dict[str, Any]] = Field(default_factory=list, description="Response sections")
    pricing_summary: dict[str, Any] = Field(default_factory=dict, description="Pricing summary breakdown")
    compliance_matrix: list[dict[str, Any]] = Field(default_factory=list, description="Compliance items")


class ComplianceMatrixItem(BaseModel):
    """Individual entry in the compliance matrix."""

    req_id: str = Field(description="Tender requirement ID (e.g. REQ-001)")
    description: str = Field(description="Text requirement description")
    type: str = Field(default="Mandatory", description="Mandatory, Scored, or Optional")
    compliance_status: str = Field(default="Compliant", description="Compliant, Partially Compliant, Non-Compliant")
    response_section: str = Field(default="Section 2", description="Proposal section covering this item")
    evidence_citation: str = Field(default="", description="Citations to case study or cert (e.g. CS-001)")


class DocumentGenerationResult(BaseModel):
    """Result returned upon document creation or modification."""

    doc_id: str = Field(description="Unique generated document identifier")
    bid_id: str
    docx_path: str
    docx_size_bytes: int
    created_at: str
    template_used: str


class PdfConversionResult(BaseModel):
    """Result returned upon PDF conversion."""

    doc_id: str
    pdf_path: str
    pdf_size_bytes: int
    converter_engine: str  # 'libreoffice' or 'fpdf2_fallback'


class DocumentDownloadInfo(BaseModel):
    """File URLs and paths for download."""

    doc_id: str
    docx_path: str | None
    docx_exists: bool
    docx_size_bytes: int
    pdf_path: str | None
    pdf_exists: bool
    pdf_size_bytes: int
    download_url_docx: str
    download_url_pdf: str
