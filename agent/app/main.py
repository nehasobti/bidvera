"""Service entry point for Bidvera Agent API."""

from __future__ import annotations

import uvicorn

from agent.app.api.main import app
from agent.app.core.settings import settings


def main() -> None:
    uvicorn.run(
        app,
        host=settings.host,
        port=settings.port,
        log_level="info",
    )


if __name__ == "__main__":
    main()
