"""Unit tests for BidState data structures and requirement reducers."""

from agent.app.graph.state import (
    BidInfo,
    EligibilityResult,
    ParsedDocument,
    RequirementItem,
    merge_requirements,
)


def test_merge_requirements_deduplication():
    initial = [
        {"id": "REQ-001", "text": "Minimum €10M turnover", "type": "Mandatory"},
        {"id": "REQ-002", "text": "ISO 27001 certificate", "type": "Mandatory"},
    ]
    incoming = [
        # Duplicate by ID
        {"id": "REQ-001", "text": "Minimum €10M turnover duplicate", "type": "Mandatory"},
        # Duplicate by Text
        {"id": "REQ-003", "text": "ISO 27001 certificate", "type": "Mandatory"},
        # New distinct requirement
        {"id": "REQ-004", "text": "Zero downtime cutover", "type": "Mandatory"},
    ]

    merged = merge_requirements(initial, incoming)
    assert len(merged) == 3
    ids = [r["id"] for r in merged]
    assert "REQ-001" in ids
    assert "REQ-002" in ids
    assert "REQ-004" in ids
    assert "REQ-003" not in ids


def test_bid_models_validation():
    bid = BidInfo(id="bid-01", tender_id="tender-001", title="Cloud Migration")
    assert bid.id == "bid-01"
    assert bid.status == "created"

    req = RequirementItem(
        id="REQ-001",
        text="Must have ISO 27001",
        type="Mandatory",
        weight="Pass/Fail",
        section="Section 3",
        page_ref="Page 4",
    )
    assert req.type == "Mandatory"

    doc = ParsedDocument(id="doc-01", name="RFP.docx", pages=10)
    assert doc.pages == 10
    assert len(doc.sections) == 0

    el = EligibilityResult(recommendation="bid", reasons=["All criteria met"])
    assert el.recommendation == "bid"
