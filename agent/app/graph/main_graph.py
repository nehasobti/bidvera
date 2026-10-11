"""Main workflow graph definition for Bidvera."""

from __future__ import annotations

from typing import Any
from langgraph.graph import END, START, StateGraph

from agent.app.core.db import get_checkpointer
from agent.app.graph.nodes.bid_decision import bid_decision_node
from agent.app.graph.nodes.calculate_pricing import calculate_pricing_node
from agent.app.graph.nodes.check_eligibility import check_eligibility_node
from agent.app.graph.nodes.draft_sections import (
    draft_section_node,
    fanout_sections_for_drafting,
    finalize_drafting_node,
)
from agent.app.graph.nodes.extract_requirements import (
    extract_section_requirements,
    fanout_sections,
    finalize_requirements_node,
)
from agent.app.graph.nodes.ingest import ingest_node
from agent.app.graph.nodes.no_bid_summary import no_bid_summary_node
from agent.app.graph.nodes.parse import parse_documents_node
from agent.app.graph.nodes.plan_outline import plan_outline_node
from agent.app.graph.state import BidState


def create_bid_graph(checkpointer: Any = None) -> Any:
    """Builds and compiles the core Bidvera StateGraph workflow."""
    builder = StateGraph(BidState)

    # 1. Register Phase 1, 2, 3, 4 Nodes
    builder.add_node("ingest", ingest_node)
    builder.add_node("parse_documents", parse_documents_node)
    builder.add_node("extract_section_requirements", extract_section_requirements)
    builder.add_node("finalize_requirements", finalize_requirements_node)
    builder.add_node("check_eligibility", check_eligibility_node)
    builder.add_node("bid_decision", bid_decision_node)
    builder.add_node("plan_outline", plan_outline_node)
    builder.add_node("no_bid_summary", no_bid_summary_node)

    # Phase 4 Nodes: Section drafting and commercial pricing
    builder.add_node("draft_section", draft_section_node)
    builder.add_node("finalize_drafting", finalize_drafting_node)
    builder.add_node("calculate_pricing", calculate_pricing_node)

    # 2. Sequential & Parallel Edges
    builder.add_edge(START, "ingest")
    builder.add_edge("ingest", "parse_documents")

    # Parallel fanout to extract requirements per section
    builder.add_conditional_edges(
        "parse_documents",
        fanout_sections,
        ["extract_section_requirements"],
    )

    # Parallel branches fan back in to finalize_requirements
    builder.add_edge("extract_section_requirements", "finalize_requirements")

    # Requirement extraction flows to eligibility checking
    builder.add_edge("finalize_requirements", "check_eligibility")

    # Eligibility evaluation flows to human bid decision checkpoint
    builder.add_edge("check_eligibility", "bid_decision")

    # If decision is 'bid', outline is planned
    # plan_outline fans out to parallel draft_section nodes
    builder.add_conditional_edges(
        "plan_outline",
        fanout_sections_for_drafting,
        ["draft_section"],
    )

    # Parallel drafting branches fan in to finalize_drafting
    builder.add_edge("draft_section", "finalize_drafting")

    # Drafted sections flow to commercial pricing calculation
    builder.add_edge("finalize_drafting", "calculate_pricing")

    # End paths
    builder.add_edge("calculate_pricing", END)
    builder.add_edge("no_bid_summary", END)

    # Compile with checkpointer
    effective_checkpointer = checkpointer if checkpointer is not None else get_checkpointer()
    return builder.compile(checkpointer=effective_checkpointer)


# Default compiled graph instance
bid_graph = create_bid_graph()
