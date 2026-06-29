"""Handler routers aggregator."""

from __future__ import annotations

from aiogram import Router


def get_routers() -> list[Router]:
    """Return all routers to register on the dispatcher, in order.

    Phase 1 exposes only the user ``/start`` router. The admin router is an
    empty placeholder for later phases.
    """
    from bot.handlers.admin import router as admin_router
    from bot.handlers.user import router as user_router

    return [user_router, admin_router]
