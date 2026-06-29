"""Application configuration.

All configuration comes from the environment / ``.env`` via pydantic-settings.
There are NO hardcoded secrets anywhere in the codebase.
"""

from __future__ import annotations

from functools import lru_cache

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Strongly-typed application settings loaded from the environment."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        case_sensitive=True,
        extra="ignore",
    )

    # --- Telegram bot --------------------------------------------------------
    BOT_TOKEN: str = Field(..., description="Telegram bot token from BotFather")
    MAIN_ADMIN_ID: int = Field(..., description="Telegram id of the main admin")
    LOG_GROUP_ID: int | None = Field(
        default=None, description="Optional Telegram group id for log forwarding"
    )

    # --- Web admin panel -----------------------------------------------------
    WEB_DOMAIN: str = Field(..., description="Public domain the panel runs on")
    WEB_ADMIN_USERNAME: str = Field(..., description="Web panel admin username")
    WEB_ADMIN_PASSWORD_HASH: str = Field(
        ..., description="Bcrypt hash of the web admin password"
    )

    # --- Database ------------------------------------------------------------
    DB_PASSWORD: str = Field(..., description="PostgreSQL password (compose)")
    DATABASE_URL: str = Field(
        ...,
        description="Async SQLAlchemy URL, e.g. postgresql+asyncpg://...",
    )

    # --- Redis ---------------------------------------------------------------
    REDIS_URL: str = Field(
        default="redis://redis:6379/0", description="Async Redis URL"
    )

    # --- Security ------------------------------------------------------------
    SECRET_KEY: str = Field(..., description="JWT/session signing secret")

    # --- Auth tuning (not secret) -------------------------------------------
    JWT_ALGORITHM: str = "HS256"
    JWT_EXPIRE_MINUTES: int = 60 * 12  # 12 hours

    @field_validator("LOG_GROUP_ID", mode="before")
    @classmethod
    def _empty_str_to_none(cls, v: object) -> object:
        """Treat an empty/blank LOG_GROUP_ID env value as unset (None)."""
        if isinstance(v, str) and v.strip() == "":
            return None
        return v

    @property
    def is_sqlite(self) -> bool:
        """True when running against a local SQLite database (dev/tests)."""
        return self.DATABASE_URL.startswith("sqlite")


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance.

    Cached so the ``.env`` file is only parsed once per process.
    """
    return Settings()  # type: ignore[call-arg]


# Convenience singleton for simple imports: ``from shared.config import settings``.
settings = get_settings()
