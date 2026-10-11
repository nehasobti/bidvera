"""State definitions and sub-states for Bidvera LangGraph workflow."""

from __future__ import annotations

import operator
from typing import Annotated, Any, Literal

from pydantic import BaseModel, Field
from typing_extensions import TypedDict


class BidInfo(BaseModel):
    """Core tender and bid metadata."""

    id: str = Field(description="Unique bid thread ID (e.g. bid-001)")
    tender_id: str = Field(description="Target tender identifier (e.g. tender-001)")
    title: str = Field(default="", description="Tender title")
    buyer: str = Field(default="", description="Procurement authority / buyer")
    deadline: str = Field(default="", description="Submission deadline ISO string")
    status: str = Field(default="created", description="Bid workflow status")


class DocumentSection(BaseModel):
    """Structured section extracted from a tender document."""

    section_id: str
    heading: str
    content: str
    page_ref: str = "Page 1"


class ParsedDocument(BaseModel):
    """Parsed tender document."""

    id: str
    name: str
    pages: int = 1
    sections: list[DocumentSection] = Field(default_factory=list)
    tables_count: int = 0


class RequirementItem(BaseModel):
    """Atomic requirement extracted from tender documents."""

    id: str = Field(description="Requirement identifier (e.g. REQ-001)")
    text: str = Field(description="Requirement description text")
    type: Literal["Mandatory", "Scored", "Optional"] = Field(default="Mandatory")
    weight: str = Field(default="Pass/Fail")
    section: str = Field(default="")
    page_ref: str = Field(default="")
    category: str = Field(default="technical")


class CriterionEvaluation(BaseModel):
    """Evaluation result for an individual eligibility criterion."""

    criterion: str
    status: Literal["met", "not_met", "unclear"]
    evidence: str
    citation: str = ""


class EligibilityResult(BaseModel):
    """Overall company eligibility evaluation."""

    recommendation: Literal["bid", "no-bid", "conditional"] = "bid"
    reasons: list[str] = Field(default_factory=list)
    criteria_results: list[CriterionEvaluation] = Field(default_factory=list)


class DecisionRecord(BaseModel):
    """Checkpoint decision entered by a human reviewer."""

    checkpoint: str  # bid_decision, pricing_approval, section_edit, final_approval
    decision: str    # bid, no_bid, approve, revise
    who: str
    when: str
    comment: str = ""


def merge_requirements(
    current: list[dict[str, Any]],
    incoming: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Reducer to merge and de-duplicate requirements extracted across parallel branches."""
    existing_ids = {r.get("id") for r in current if r.get("id")}
    existing_texts = {r.get("text", "").lower().strip() for r in current}

    merged = list(current)
    for inc in incoming:
        inc_id = inc.get("id")
        inc_text = inc.get("text", "").lower().strip()

        # Deduplicate by ID or identical text
        if inc_id and inc_id in existing_ids:
            continue
        if inc_text and inc_text in existing_texts:
            continue

        merged.append(inc)
        if inc_id:
            existing_ids.add(inc_id)
        if inc_text:
            existing_texts.add(inc_text)

    return merged


def merge_sections(
    current: list[dict[str, Any]],
    incoming: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Reducer to merge parallel drafted section branches."""
    existing_ids = {s.get("section_id") for s in current if s.get("section_id")}
    merged = list(current)
    for inc in incoming:
        sec_id = inc.get("section_id")
        if sec_id and sec_id in existing_ids:
            # Replace existing section with updated draft
            merged = [inc if s.get("section_id") == sec_id else s for s in merged]
        else:
            merged.append(inc)
            if sec_id:
                existing_ids.add(sec_id)
    return merged


class BidState(TypedDict):
    """Global state container for a single bid workflow thread."""

    # 1. Bid metadata
    bid: dict[str, Any]

    # 2. Parsed documents
    documents: list[dict[str, Any]]

    # 3. Requirements (merged from parallel extraction branches via reducer)
    requirements: Annotated[list[dict[str, Any]], merge_requirements]

    # 4. Eligibility evaluation
    eligibility: dict[str, Any]

    # 5. Human decisions history
    decisions: Annotated[list[dict[str, Any]], operator.add]

    # 6. Response outline & mapped requirements
    outline: list[dict[str, Any]]

    # 7. Drafted sections (merged from parallel drafting branches via reducer)
    sections: Annotated[list[dict[str, Any]], merge_sections]

    # 8. Commercial pricing
    pricing: dict[str, Any]

    # 9. Review findings
    review: dict[str, Any]

    # 10. Compliance matrix
    compliance_matrix: list[dict[str, Any]]

    # 11. Generated document artifacts (DOCX, PDF)
    artifacts: dict[str, Any]

    # 12. Lifecycle status and progress
    status: str
    error: str | None
