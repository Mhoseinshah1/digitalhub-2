"""Bot and dispatcher factory.

Wires the aiogram Bot, a Redis-backed FSM storage, middlewares and routers.
"""

from __future__ import annotations

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.fsm.storage.redis import RedisStorage

from shared.config import settings
from shared.redis import get_redis


def build_bot() -> Bot:
    """Create the aiogram Bot with sane defaults (HTML parse mode)."""
    return Bot(
        token=settings.BOT_TOKEN,
        default=DefaultBotProperties(parse_mode=ParseMode.HTML),
    )


def build_dispatcher() -> Dispatcher:
    """Create the Dispatcher with Redis FSM storage, middlewares and routers."""
    storage = RedisStorage(redis=get_redis())
    dp = Dispatcher(storage=storage)

    # Middlewares (Phase 1: stubs only).
    from bot.middlewares.auth import AuthMiddleware
    from bot.middlewares.throttling import ThrottlingMiddleware

    dp.update.outer_middleware(AuthMiddleware())
    dp.update.outer_middleware(ThrottlingMiddleware())

    # Routers.
    from bot.handlers import get_routers

    for router in get_routers():
        dp.include_router(router)

    return dp
