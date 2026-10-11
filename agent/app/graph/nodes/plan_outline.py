"""Node: Outline Planner mapping requirements to structured proposal sections."""

from __future__ import annotations

from typing import Any
from agent.app.graph.state import BidState


async def plan_outline_node(state: BidState) -> dict[str, Any]:
    """Generates the proposal structure and maps extracted requirements to sections."""
    requirements = state.get("requirements", [])

    # Categorize requirement IDs
    sec1_reqs: list[str] = []
    sec2_reqs: list[str] = []
    sec3_reqs: list[str] = []
    sec4_reqs: list[str] = []
    sec5_reqs: list[str] = []

    for req in requirements:
        rid = req.get("id", "")
        text = req.get("text", "").lower()

        if "turnover" in text or "history" in text or "experience" in text:
            sec1_reqs.append(rid)
        elif "security" in text or "iso" in text or "27001" in text or "encrypt" in text or "compliance" in text:
            sec3_reqs.append(rid)
        elif "gitops" in text or "pipeline" in text or "argocd" in text or "ci/cd" in text:
            sec4_reqs.append(rid)
        elif "sla" in text or "support" in text or "hypercare" in text:
            sec5_reqs.append(rid)
        else:
            sec2_reqs.append(rid)

    outline = [
        {
            "id": "sec-001",
            "section_number": 1,
            "title": "Executive Summary & Bidder Qualifications",
            "description": "Executive overview of the proposal, corporate background, and eligibility proof.",
            "mapped_requirements": sec1_reqs,
            "word_limit": 600,
        },
        {
            "id": "sec-002",
            "section_number": 2,
            "title": "Technical Architecture & Transformation Strategy",
            "description": "Proposed system topology, workload migration phases, and zero-downtime cutover plan.",
            "mapped_requirements": sec2_reqs,
            "word_limit": 1500,
        },
        {
            "id": "sec-003",
            "section_number": 3,
            "title": "Information Security, Governance & Regulatory Compliance",
            "description": "ISO 27001 ISMS policies, CIS Benchmark Level 2 controls, data encryption, and GDPR compliance.",
            "mapped_requirements": sec3_reqs,
            "word_limit": 1000,
        },
        {
            "id": "sec-004",
            "section_number": 4,
            "title": "DevOps Automation, Container Platform & GitOps Delivery",
            "description": "Amazon EKS container ecosystem, ArgoCD GitOps deployment manifests, and observability.",
            "mapped_requirements": sec4_reqs,
            "word_limit": 1000,
        },
        {
            "id": "sec-005",
            "section_number": 5,
            "title": "Project Governance, SLA Commitments & Hypercare Support",
            "description": "Team staffing model, agile delivery cadence, 15-minute P1 incident response, and hypercare.",
            "mapped_requirements": sec5_reqs,
            "word_limit": 800,
        },
        {
            "id": "sec-006",
            "section_number": 6,
            "title": "Comprehensive Compliance Matrix & Verification Declarations",
            "description": "Traceability matrix mapping every mandatory and scored RFP requirement to proposal evidence.",
            "mapped_requirements": [r.get("id", "") for r in requirements],
            "word_limit": 500,
        },
    ]

    return {
        "outline": outline,
        "status": "outline_planned",
    }
