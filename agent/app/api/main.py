"""FastAPI Application factory for Bidvera Agent Service."""

from __future__ import annotations

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from agent.app.api.bids import router as bids_router
from agent.app.core.settings import settings


def create_app() -> FastAPI:
    """Builds and configures the FastAPI application."""
    app = FastAPI(
        title=settings.app_name,
        version="0.1.0",
        description="Bidvera: Multi-agent tender response system API",
    )

    # Enable CORS for Next.js frontend
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Register routers
    app.include_router(bids_router)

    @app.get("/health")
    async def health_check():
        return {
            "status": "healthy",
            "service": "agent-api",
            "version": "0.1.0",
            "llm_provider": settings.llm_provider,
        }

    return app


app = create_app()
