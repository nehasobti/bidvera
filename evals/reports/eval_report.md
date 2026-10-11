# Bidvera Evaluation Benchmark Report

**Suite:** `QUICK`  
**Date:** 2026-10-11 20:00:18  
**Status:** ALL TARGETS SATISFIED

---

## 1. Executive Summary & Target Metrics

| Metric | Target | Achieved (quick) | Status |
|---|---|---|---|
| **Requirement Extraction Recall** | $\ge 0.90$ | **1.0** | PASSED |
| **Eligibility Accuracy** | $\ge 0.90$ | **1.0** | PASSED |
| **Proposal Coverage** | $100\%$ | **100.0%** | PASSED |
| **Citation Grounding Support** | $\ge 0.95$ | **1.0** | PASSED |
| **Hallucinated Facts** | $0$ | **0** | PASSED |
| **Tender Q&A Accuracy** | $\ge 0.85$ | **1.0** | PASSED |
| **Guardrails & Trap Pass Rate** | $100\%$ | **100.0%** | PASSED |

---

## 2. Tender Evaluation Breakdown

| Tender ID | Requirements Extracted | Recall | Precision | Coverage | Citations | Duration (s) |
|---|---|---|---|---|---|---|
| `tender-001` | 6 | 1.0 | 1.0 | 1.0 | 1.0 | 0.64s |

---

## 3. Tender Q&A Benchmarks

- **Questions Tested:** 10
- **Answer & Citation Accuracy:** 100.0%

---

## 4. Security Guardrails & Trap Cases

- **Cases Evaluated:** 8
- **Prompt Injection Defense:** Verified (Tender documents treated strictly as untrusted data)
- **Role Permissions & Loop Limits:** Maximum review cycles enforced ($\le 2$)
