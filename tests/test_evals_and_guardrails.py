"""Test suite verifying evaluation benchmarks, guardrails, and trap defenses."""

import pytest
from evals.metrics import (
    calculate_citation_support,
    calculate_coverage,
    calculate_eligibility_accuracy,
    calculate_extraction_metrics,
    count_hallucinated_facts,
)
from evals.runner import run_evals


@pytest.mark.asyncio
async def test_quick_eval_suite_passes_all_targets():
    """Verify that quick eval suite runs and all benchmark targets pass."""
    summary = await run_evals(suite="quick")
    assert summary["avg_recall"] >= 0.90
    assert summary["avg_eligibility"] >= 0.90
    assert summary["avg_coverage"] >= 0.90
    assert summary["avg_citation"] >= 0.95
    assert summary["total_hallucinations"] == 0
    assert summary["qa_accuracy"] >= 0.85
    assert summary["trap_pass_rate"] >= 0.95


def test_metric_calculations_unit():
    """Verify unit calculations for extraction metrics, coverage, and citation grounding."""
    gold = [{"id": "REQ-1", "text": "Must have ISO 27001 and €10M turnover"}]
    extracted = [{"id": "R1", "text": "Bidders must have ISO 27001 and €10M turnover"}]

    metrics = calculate_extraction_metrics(extracted, gold)
    assert metrics["recall"] == 1.0
    assert metrics["precision"] == 1.0

    # Eligibility test
    assert calculate_eligibility_accuracy({"recommendation": "bid"}, {"recommendation": "bid"}) == 1.0
    assert calculate_eligibility_accuracy({"recommendation": "no-bid"}, {"recommendation": "bid"}) == 0.0

    # Coverage test
    matrix = [{"compliance_status": "Compliant"}, {"compliance_status": "Partial"}]
    assert calculate_coverage(matrix) == 1.0

    # Citation test
    sections = [
        {"citations": ["Tychon KB"]},
        {"content": "Tychon delivers [NEEDS INPUT: specific detail]"},
    ]
    assert calculate_citation_support(sections) == 1.0

    # Hallucination test
    assert count_hallucinated_facts([{"content": "Tychon has 285 engineers"}]) == 0
    assert count_hallucinated_facts([{"content": "Tychon has 15,000 engineers"}]) == 1
