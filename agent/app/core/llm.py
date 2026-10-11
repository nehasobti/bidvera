"""LLM Model Factory supporting Claude, Gemini, OpenAI, and deterministic test models."""

from __future__ import annotations

import json
from typing import Any

from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import AIMessage, BaseMessage
from langchain_core.outputs import ChatGeneration, ChatResult

from agent.app.core.settings import settings


class DeterministicChatModel(BaseChatModel):
    """Deterministic Chat Model for tests and offline development without API keys."""

    def _generate(
        self,
        messages: list[BaseMessage],
        stop: list[str] | None = None,
        run_manager: Any = None,
        **kwargs: Any,
    ) -> ChatResult:
        last_msg = messages[-1].content if messages else ""
        last_str = str(last_msg).lower()
        content = "OK"

        # Check section drafting FIRST so "Mapped Requirements:" does not trigger requirement extraction
        if "section title:" in last_str or "draft a comprehensive" in last_str:
            title_line = [line for line in str(last_msg).split("\n") if "section title:" in line.lower()]
            sec_title = title_line[0].split(":", 1)[1].strip() if title_line else "Technical Section"
            content = (
                f"### 1. Strategic Context & Alignment\n"
                f"Tychon Software brings mature enterprise delivery capabilities directly aligned with the requirements for {sec_title}. "
                f"Our certified engineering practices and battle-tested methodology ensure robust, zero-disruption delivery adhering to international standards.\n\n"
                f"### 2. Technical Approach & Solution Architecture\n"
                f"Our multidisciplinary teams leverage modular infrastructure as code, automated testing pipelines, and strict security baselines. "
                f"Every deliverable is integrated through continuous verification gates to achieve high reliability and strict compliance.\n\n"
                f"- **Architecture & Standards:** Built upon CIS Benchmark Level 2 controls and verified AWS Well-Architected Framework principles.\n"
                f"- **Delivery Velocity:** Iterative sprint execution paired with automated smoke suites to accelerate turnaround while mitigating production risks.\n"
                f"- **Quality Assurance:** Mandatory peer reviews, automated unit and integration tests with zero regression tolerance.\n\n"
                f"### 3. Traceability & Governance\n"
                f"All mapped requirements are continuously traced through our automated compliance matrix, ensuring full audit readiness and SLA adherence across all operational phases."
            )
        # If user/system prompt asked for JSON requirement extraction
        elif "extract" in last_str or "extract_requirements" in last_str or "atomic requirement" in last_str:
            content = json.dumps({
                "requirements": [
                    {
                        "id": "REQ-001",
                        "text": "Bidders must demonstrate minimum turnover and 8 years operational history",
                        "type": "Mandatory",
                        "weight": "Pass/Fail",
                        "section": "Section 3.1",
                        "page_ref": "Page 3",
                        "category": "eligibility",
                    },
                    {
                        "id": "REQ-002",
                        "text": "Provide valid ISO/IEC 27001 accreditation certificate",
                        "type": "Mandatory",
                        "weight": "Pass/Fail",
                        "section": "Section 3.2",
                        "page_ref": "Page 4",
                        "category": "security",
                    },
                    {
                        "id": "REQ-003",
                        "text": "Zero unplanned downtime during migration cutover",
                        "type": "Mandatory",
                        "weight": "25%",
                        "section": "Section 2.3",
                        "page_ref": "Page 7",
                        "category": "technical",
                    },
                ]
            })
        elif "eligibility" in str(last_msg).lower():
            content = json.dumps({
                "recommendation": "bid",
                "reasons": [
                    "Tychon Software has €18.5M turnover (exceeds €10M requirement).",
                    "Active ISO 27001:2022 accreditation verified through August 2027.",
                    "AWS Premier Tier Partner status is active with proven migration competency.",
                ],
                "criteria_results": [
                    {
                        "criterion": "Annual Turnover >= €10M",
                        "status": "met",
                        "evidence": "Tychon Software annual turnover is €18.5M (2025)",
                        "citation": "profile.financials",
                    },
                    {
                        "criterion": "ISO 27001 Certification",
                        "status": "met",
                        "evidence": "Active ISO/IEC 27001:2022 cert 12 104 59281 TMS",
                        "citation": "CERT-ISO-27001",
                    },
                ],
            })

        message = AIMessage(content=content)
        generation = ChatGeneration(message=message)
        return ChatResult(generations=[generation])

    @property
    def _llm_type(self) -> str:
        return "deterministic-test-llm"


def get_llm(tier: str = "fast") -> BaseChatModel:
    """Returns configured LangChain ChatModel based on provider and tier ('planner' or 'fast')."""
    provider = settings.llm_provider.lower().strip()

    if provider == "fake":
        return DeterministicChatModel()

    if provider == "openai":
        from langchain_openai import ChatOpenAI
        model_name = "gpt-4o" if tier == "planner" else "gpt-4o-mini"
        return ChatOpenAI(
            model=model_name,
            api_key=settings.openai_api_key,
            temperature=0.1,
        )

    if provider == "anthropic":
        from langchain_anthropic import ChatAnthropic
        model_name = "claude-3-5-sonnet-20241022" if tier == "planner" else "claude-3-5-haiku-20241022"
        return ChatAnthropic(
            model=model_name,
            api_key=settings.anthropic_api_key,
            temperature=0.1,
        )

    if provider in ("google", "gemini"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        model_name = "gemini-1.5-pro" if tier == "planner" else "gemini-1.5-flash"
        return ChatGoogleGenerativeAI(
            model=model_name,
            google_api_key=settings.google_api_key,
            temperature=0.1,
        )

    # Fallback to deterministic model
    return DeterministicChatModel()
