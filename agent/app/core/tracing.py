"""Observability and tracing integration with Langfuse."""

from __future__ import annotations

import logging
from typing import Any

from agent.app.core.settings import settings

logger = logging.getLogger(__name__)


def get_tracing_callbacks(session_id: str | None = None, tags: list[str] | None = None) -> list[Any]:
    """Returns Langfuse or LangChain callback handlers if configured."""
    callbacks: list[Any] = []

    if settings.langfuse_public_key and settings.langfuse_secret_key:
        try:
            from langfuse.callback import CallbackHandler
            handler = CallbackHandler(
                public_key=settings.langfuse_public_key,
                secret_key=settings.langfuse_secret_key,
                host=settings.langfuse_host,
                session_id=session_id,
                tags=tags or ["bidvera"],
            )
            callbacks.append(handler)
            logger.info("Langfuse tracing handler initialized.")
        except Exception as e:
            logger.warning(f"Could not initialize Langfuse handler: {e}")

    return callbacks
