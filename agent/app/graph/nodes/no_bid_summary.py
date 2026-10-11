"""Node: Summarizes no-bid decision rationale and concludes the run."""

from __future__ import annotations

from typing import Any
from agent.app.graph.state import BidState


async def no_bid_summary_node(state: BidState) -> dict[str, Any]:
    """Generates concluding audit log when bid manager decides not to pursue the tender."""
    decisions = state.get("decisions", [])
    latest_decision = decisions[-1] if decisions else {}

    reasons = state.get("eligibility", {}).get("reasons", [])
    comment = latest_decision.get("comment", "")

    summary_text = (
        f"Bid pursuit concluded as NO-BID by {latest_decision.get('who', 'bid_manager')}. "
        f"Commentary: '{comment}'. Criteria evaluation: {'; '.join(reasons)}."
    )

    return {
        "status": "no_bid_concluded",
        "review": {
            "no_bid_summary": summary_text,
        },
    }
