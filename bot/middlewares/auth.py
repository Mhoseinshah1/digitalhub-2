"""Auth middleware (stub).

Phase 1: pass-through. Later phases will resolve the DB user, attach it to the
handler data, and enforce blocking/admin checks here.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject


class AuthMiddleware(BaseMiddleware):
    """Resolve/attach the current user (no-op in Phase 1)."""

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # TODO(phase-2): load user via UserService, block if is_blocked.
        return await handler(event, data)
