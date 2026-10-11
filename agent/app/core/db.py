"""Checkpointer persistence factory for LangGraph workflows."""

from __future__ import annotations

import logging

from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.checkpoint.memory import MemorySaver

from agent.app.core.settings import settings

logger = logging.getLogger(__name__)

# Global singleton in-memory checkpointer for fallback and test execution
_in_memory_checkpointer = MemorySaver()


def get_checkpointer() -> BaseCheckpointSaver:
    """Returns a PostgresSaver if DATABASE_URL is configured and reachable,

    otherwise falls back gracefully to in-memory MemorySaver.
    """
    db_url = settings.database_url
    if db_url and "postgresql" in db_url:
        try:
            from langgraph.checkpoint.postgres import PostgresSaver
            # Initialize PostgresSaver
            saver = PostgresSaver.from_conn_string(db_url)
            saver.setup()
            logger.info("Successfully connected to PostgreSQL checkpointer.")
            return saver
        except Exception as e:
            logger.warning(
                f"Failed to connect to PostgreSQL checkpointer ({e}). Falling back to in-memory saver."
            )

    return _in_memory_checkpointer
