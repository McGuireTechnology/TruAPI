from __future__ import annotations
from pydantic import Field
from pydantic_settings import BaseSettings
from truapi.shared.settings.utilities import create_settings_config
s"""Database configuration settings."""


class DatabaseSettings(BaseSettings):
    """Database configuration settings."""

    model_config = create_settings_config("DB_")

    # Connection configuration
    url: str = Field(
        default="sqlite:///:memory:",
        description="Database connection URL"
    )
    echo: bool = Field(default=False, description="Log all SQL statements")
    pool_size: int = Field(default=5, description="Connection pool size")
    max_overflow: int = Field(
        default=10, description="Max overflow connections")

    # Repository backend (applies to all modules)
    repository_backend: str = Field(
        default="inmemory",
        description="Repository implementation: inmemory or sqlalchemy"
    )


__all__ = ["DatabaseSettings"]
