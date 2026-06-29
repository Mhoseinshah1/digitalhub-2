"""Create (or ensure) the main admin user.

Run after migrations:

    python -m scripts.create_admin

Reads ``MAIN_ADMIN_ID`` from the environment via shared.config and upserts a
user row with the admin role. Idempotent.
"""

from __future__ import annotations

import asyncio
import logging

from shared.config import settings
from shared.database import get_session
from shared.services.user import UserService

logging.basicConfig(level=logging.INFO, format="%(message)s")
logger = logging.getLogger("create_admin")


async def _main() -> None:
    async with get_session() as session:
        service = UserService(session)
        user = await service.ensure_main_admin()
    logger.info(
        "Main admin ensured: telegram_id=%s role=%s",
        user.telegram_id,
        user.role.value,
    )


def main() -> None:
    logger.info("Ensuring main admin (id=%s)…", settings.MAIN_ADMIN_ID)
    asyncio.run(_main())


if __name__ == "__main__":
    main()
