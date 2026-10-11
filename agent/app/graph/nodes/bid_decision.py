"""Node: Human checkpoint interrupt for bid/no-bid decision."""

from __future__ import annotations

import datetime
from typing import Any, Literal
from langgraph.types import Command, interrupt

from agent.app.graph.state import BidState, DecisionRecord


def bid_decision_node(state: BidState) -> Command[Literal["plan_outline", "no_bid_summary"]]:
    """Pauses workflow execution with interrupt() to request human bid/no-bid approval."""
    eligibility = state.get("eligibility", {})
    recommendation = eligibility.get("recommendation", "bid")
    reasons = eligibility.get("reasons", [])

    # Interrupt execution and wait for human response
    human_input = interrupt({
        "type": "bid_decision",
        "title": "Bid / No-Bid Decision Required",
        "recommendation": recommendation,
        "reasons": reasons,
        "criteria": eligibility.get("criteria_results", []),
    })

    # Unpack human decision
    if not isinstance(human_input, dict):
        human_input = {"decision": "bid", "comment": str(human_input)}

    decision = str(human_input.get("decision", "bid")).lower().strip()
    comment = str(human_input.get("comment", ""))
    who = str(human_input.get("who", "bid_manager"))

    decision_record = DecisionRecord(
        checkpoint="bid_decision",
        decision=decision,
        who=who,
        when=datetime.datetime.now().isoformat(),
        comment=comment,
    ).model_dump()

    if decision in ("no-bid", "no_bid", "reject"):
        return Command(
            goto="no_bid_summary",
            update={
                "status": "no_bid_decided",
                "decisions": [decision_record],
            },
        )

    return Command(
        goto="plan_outline",
        update={
            "status": "bid_approved",
            "decisions": [decision_record],
        },
    )
