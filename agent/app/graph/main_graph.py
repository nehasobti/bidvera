"""Main workflow graph definition for Bidvera."""

from __future__ import annotations

from typing import Any

from langgraph.graph import END, START, StateGraph

from agent.app.core.db import get_checkpointer
from agent.app.graph.nodes.check_eligibility import check_eligibility_node
from agent.app.graph.nodes.extract_requirements import (
    extract_section_requirements,
    fanout_sections,
    finalize_requirements_node,
)
from agent.app.graph.nodes.ingest import ingest_node
from agent.app.graph.nodes.parse import parse_documents_node
from agent.app.graph.state import BidState


def create_bid_graph(checkpointer: Any = None) -> Any:
    """Builds and compiles the core Bidvera StateGraph workflow."""
    builder = StateGraph(BidState)

    # 1. Register Nodes
    builder.add_node("ingest", ingest_node)
    builder.add_node("parse_documents", parse_documents_node)
    builder.add_node("extract_section_requirements", extract_section_requirements)
    builder.add_node("finalize_requirements", finalize_requirements_node)
    builder.add_node("check_eligibility", check_eligibility_node)

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
    builder.add_edge("check_eligibility", END)

    # Compile with checkpointer
    effective_checkpointer = checkpointer if checkpointer is not None else get_checkpointer()
    return builder.compile(checkpointer=effective_checkpointer)


# Default compiled graph instance
bid_graph = create_bid_graph()
