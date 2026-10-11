"""MCP Client abstraction with per-agent tool allowlists."""

from __future__ import annotations

import importlib.util
import json
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)

# Agent Tool Allowlists specified by technical architecture
AGENT_TOOL_ALLOWLISTS: dict[str, list[str]] = {
    "tender_finder": ["search_tenders", "get_tender", "list_documents", "get_document"],
    "requirement_extractor": [],  # Works on parsed text
    "eligibility_checker": ["get_profile", "list_certifications", "find_case_studies", "search_knowledge"],
    "outline_planner": [],
    "section_writer": ["search_knowledge", "find_case_studies", "get_cv"],
    "pricing_analyst": ["get_rate_card", "estimate_effort", "build_price_sheet"],
    "reviewer": ["search_knowledge"],
    "assembler": ["create_response_doc", "add_compliance_matrix", "convert_to_pdf", "get_download_url"],
    "tender_qa": ["search_knowledge"],
}

# Server names mapping
SERVER_TOOLS_MAP: dict[str, str] = {
    "search_tenders": "tender-search",
    "get_tender": "tender-search",
    "list_documents": "tender-search",
    "get_document": "tender-search",
    "get_profile": "company-knowledge",
    "search_knowledge": "company-knowledge",
    "find_case_studies": "company-knowledge",
    "list_certifications": "company-knowledge",
    "get_cv": "company-knowledge",
    "get_rate_card": "pricing",
    "estimate_effort": "pricing",
    "build_price_sheet": "pricing",
    "create_response_doc": "documents",
    "add_compliance_matrix": "documents",
    "convert_to_pdf": "documents",
    "get_download_url": "documents",
}

BASE_DIR = Path(__file__).resolve().parent.parent.parent

# Cache of loaded FastMCP server objects
_SERVER_INSTANCES: dict[str, Any] = {}


def _get_server_mcp(server_name: str) -> Any:
    if server_name in _SERVER_INSTANCES:
        return _SERVER_INSTANCES[server_name]

    server_dir = BASE_DIR / "mcp-servers" / server_name
    server_file = server_dir / "server.py"
    if not server_file.exists():
        raise FileNotFoundError(f"MCP server file not found: {server_file}")

    parent_str = str(server_dir)
    if parent_str not in sys.path:
        sys.path.insert(0, parent_str)

    mod_name = f"mcp_server_{server_name.replace('-', '_')}"
    spec = importlib.util.spec_from_file_location(mod_name, server_file)
    if spec is None or spec.loader is None:
        raise ImportError(f"Cannot load module from {server_file}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    mcp_obj = getattr(mod, "mcp")
    _SERVER_INSTANCES[server_name] = mcp_obj
    return mcp_obj


async def call_mcp_tool(
    agent_name: str,
    tool_name: str,
    arguments: dict[str, Any],
) -> Any:
    """Invokes an MCP tool verifying agent allowlist compliance.

    Falls back to direct in-process FastMCP execution if running locally/offline.
    """
    allowed_tools = AGENT_TOOL_ALLOWLISTS.get(agent_name, [])
    if tool_name not in allowed_tools:
        raise PermissionError(
            f"Security policy violation: Agent '{agent_name}' is not authorized to call MCP tool '{tool_name}'."
        )

    server_name = SERVER_TOOLS_MAP.get(tool_name)
    if not server_name:
        raise ValueError(f"Unknown MCP tool '{tool_name}'")

    mcp = _get_server_mcp(server_name)
    res = await mcp.call_tool(tool_name, arguments)

    # Extract JSON or raw Python result
    if isinstance(res, tuple) and len(res) >= 2 and isinstance(res[1], dict) and "result" in res[1]:
        return res[1]["result"]

    blocks = res[0] if isinstance(res, (tuple, list)) else [res]
    if isinstance(blocks, list) and len(blocks) > 0:
        first_text = blocks[0].text
        try:
            return json.loads(first_text)
        except Exception:
            return first_text

    return res


async def call_fastmcp_tool(
    server_name: str,
    tool_name: str,
    arguments: dict[str, Any],
) -> Any:
    """Direct helper to call an MCP tool on a named server."""
    mcp = _get_server_mcp(server_name)
    res = await mcp.call_tool(tool_name, arguments)

    if isinstance(res, tuple) and len(res) >= 2 and isinstance(res[1], dict) and "result" in res[1]:
        return res[1]["result"]

    blocks = res[0] if isinstance(res, (tuple, list)) else [res]
    if isinstance(blocks, list) and len(blocks) > 0 and hasattr(blocks[0], "text"):
        first_text = blocks[0].text
        try:
            return json.loads(first_text)
        except Exception:
            return first_text

    return res

