"""Throttling middleware (stub).

Phase 1: pass-through. Later phases will rate-limit per user using Redis.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class ThrottlingMiddleware(BaseMiddleware):
    """Per-user rate limiting (no-op in Phase 1)."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # TODO(phase-2): Redis token-bucket per user id.
        return await handler(event, data)
