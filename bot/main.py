"""Bot entrypoint.

Boots the aiogram bot in long-polling mode. Phase 1: only ``/start`` works.
"""

from __future__ import annotations

import asyncio
import logging

from aiogram import Bot, Dispatcher

from bot.core import build_bot, build_dispatcher, setup_logging
from shared.redis import close_redis

logger = logging.getLogger("bot")


async def _run(bot: Bot, dp: Dispatcher) -> None:
    """Start polling and clean up on shutdown."""
    me = await bot.get_me()
    logger.info("Bot started as @%s (id=%s)", me.username, me.id)
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        await close_redis()


def main() -> None:
    """Synchronous entrypoint used by Docker / CLI."""
    setup_logging()
    bot = build_bot()
    dp = build_dispatcher()
    asyncio.run(_run(bot, dp))


if __name__ == "__main__":
    main()
