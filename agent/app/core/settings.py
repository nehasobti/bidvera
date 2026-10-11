"""Application configuration settings for Bidvera Agent service."""

from __future__ import annotations

import os

from pydantic import BaseModel, Field


class Settings(BaseModel):
    """Runtime configuration sourced from environment variables with sensible defaults."""

    app_name: str = "Bidvera Agent Service"
    environment: str = Field(default_factory=lambda: os.getenv("ENV", "development"))
    host: str = Field(default_factory=lambda: os.getenv("HOST", "0.0.0.0"))
    port: int = Field(default_factory=lambda: int(os.getenv("PORT", "8000")))

    # MCP Security Token
    mcp_auth_token: str = Field(default_factory=lambda: os.getenv("MCP_AUTH_TOKEN", "bidvera-dev-token"))

    # MCP Server URLs
    tender_search_url: str = Field(
        default_factory=lambda: os.getenv("TENDER_SEARCH_URL", "http://localhost:8001/sse")
    )
    company_knowledge_url: str = Field(
        default_factory=lambda: os.getenv("COMPANY_KNOWLEDGE_URL", "http://localhost:8002/sse")
    )
    pricing_url: str = Field(
        default_factory=lambda: os.getenv("PRICING_URL", "http://localhost:8003/sse")
    )
    documents_url: str = Field(
        default_factory=lambda: os.getenv("DOCUMENTS_URL", "http://localhost:8004/sse")
    )

    # Database & Persistence
    database_url: str | None = Field(default_factory=lambda: os.getenv("DATABASE_URL", None))

    # LLM Settings
    llm_provider: str = Field(default_factory=lambda: os.getenv("LLM_PROVIDER", "fake"))
    openai_api_key: str | None = Field(default_factory=lambda: os.getenv("OPENAI_API_KEY", None))
    anthropic_api_key: str | None = Field(default_factory=lambda: os.getenv("ANTHROPIC_API_KEY", None))
    google_api_key: str | None = Field(default_factory=lambda: os.getenv("GOOGLE_API_KEY", None))

    # Langfuse Tracing
    langfuse_public_key: str | None = Field(default_factory=lambda: os.getenv("LANGFUSE_PUBLIC_KEY", None))
    langfuse_secret_key: str | None = Field(default_factory=lambda: os.getenv("LANGFUSE_SECRET_KEY", None))
    langfuse_host: str = Field(
        default_factory=lambda: os.getenv("LANGFUSE_HOST", "http://localhost:3001")
    )


settings = Settings()
