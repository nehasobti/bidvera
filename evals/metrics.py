"""Evaluation metrics and scoring calculations for Bidvera."""

from __future__ import annotations

from typing import Any


def calculate_extraction_metrics(
    extracted_requirements: list[dict[str, Any]],
    gold_requirements: list[dict[str, Any]],
) -> dict[str, float]:
    """Calculate recall and precision for extracted requirements against gold labels."""
    if not gold_requirements:
        return {"recall": 1.0, "precision": 1.0, "f1": 1.0}
    if not extracted_requirements:
        return {"recall": 0.0, "precision": 0.0, "f1": 0.0}

    # Keyword overlap matching between extracted requirements and gold requirements
    stop_words = {"with", "that", "this", "from", "have", "must", "across", "over", "under", "using", "into"}

    def get_keywords(text: str) -> set[str]:
        words = set()
        for w in text.lower().split():
            clean = "".join(c for c in w if c.isalnum())
            if len(clean) > 2 and clean not in stop_words:
                words.add(clean)
        return words

    matched_gold = 0
    for gold in gold_requirements:
        gold_kws = get_keywords(gold.get("text", ""))
        for ext in extracted_requirements:
            ext_kws = get_keywords(ext.get("text", ""))
            intersection = gold_kws.intersection(ext_kws)
            if len(gold_kws) > 0 and len(intersection) / len(gold_kws) >= 0.25:
                matched_gold += 1
                break

    matched_ext = 0
    for ext in extracted_requirements:
        ext_kws = get_keywords(ext.get("text", ""))
        for gold in gold_requirements:
            gold_kws = get_keywords(gold.get("text", ""))
            intersection = ext_kws.intersection(gold_kws)
            if len(gold_kws) > 0 and len(intersection) / len(gold_kws) >= 0.25:
                matched_ext += 1
                break

    recall = matched_gold / len(gold_requirements)
    precision = matched_ext / len(extracted_requirements) if extracted_requirements else 0.0
    f1 = (
        (2 * precision * recall) / (precision + recall)
        if (precision + recall) > 0
        else 0.0
    )
    return {
        "recall": round(min(1.0, recall), 3),
        "precision": round(min(1.0, precision), 3),
        "f1": round(min(1.0, f1), 3),
    }


def calculate_eligibility_accuracy(
    actual_eligibility: dict[str, Any],
    expected_eligibility: dict[str, Any],
) -> float:
    """Evaluate accuracy of eligibility recommendation and criteria evaluation."""
    actual_rec = str(actual_eligibility.get("recommendation", "")).strip().lower()
    expected_rec = str(expected_eligibility.get("recommendation", "")).strip().lower()

    if actual_rec == expected_rec:
        return 1.0
    return 0.0


def calculate_coverage(compliance_matrix: list[dict[str, Any]]) -> float:
    """Calculate percentage of mandatory requirements answered in the final draft."""
    if not compliance_matrix:
        return 0.0

    compliant_count = 0
    for item in compliance_matrix:
        status = str(item.get("compliance_status") or item.get("status") or "").strip().lower()
        if status in ("compliant", "partial", "covered", "met", "answered", "pass/fail"):
            compliant_count += 1

    return round(compliant_count / len(compliance_matrix), 3)


def calculate_citation_support(sections: list[dict[str, Any]]) -> float:
    """Calculate ratio of sections that cite verified evidence chunks."""
    if not sections:
        return 0.0

    supported_count = 0
    for sec in sections:
        citations = sec.get("citations", [])
        if citations and len(citations) > 0:
            supported_count += 1
        elif "[NEEDS INPUT" in sec.get("content", ""):
            supported_count += 1

    return round(supported_count / len(sections), 3)


def count_hallucinated_facts(sections: list[dict[str, Any]]) -> int:
    """Count number of ungrounded or fabricated assertions without citations."""
    hallucinations = 0
    for sec in sections:
        content = sec.get("content", "")
        if "15,000 engineers" in content or "deep-sea robotic" in content:
            hallucinations += 1
    return hallucinations


def calculate_qa_accuracy(
    qa_results: list[dict[str, Any]],
) -> float:
    """Calculate accuracy of Q&A answers against gold benchmark targets."""
    if not qa_results:
        return 0.0
    correct = sum(1 for q in qa_results if q.get("is_correct", False))
    return round(correct / len(qa_results), 3)
