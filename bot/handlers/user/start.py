"""/start handler.

The only handler in Phase 1. It registers the user (via the service layer —
no business logic in the handler) and sends a Persian welcome message.
"""

from __future__ import annotations

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message

from bot.keyboards.main_menu import main_menu_keyboard
from shared.database import get_session
from shared.services.user import UserService

router = Router(name="user.start")

# User-facing Persian text (ready to move into a locale file later).
WELCOME_TEXT = (
    "👋 به <b>فروشگاه اپ‌استور</b> خوش آمدید!\n\n"
    "اینجا می‌توانید <b>اپل آیدی</b> و <b>اکانت VPN</b> تهیه کنید.\n"
    "این ربات در حال حاضر در مرحله راه‌اندازی اولیه است و به‌زودی "
    "امکانات کامل خرید فعال خواهد شد. 🌹"
)


@router.message(CommandStart())
async def handle_start(message: Message) -> None:
    """Register the user and greet them in Persian."""
    if message.from_user is None:  # defensive; channel posts etc.
        return

    async with get_session() as session:
        service = UserService(session)
        await service.get_or_create(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
        )

    await message.answer(WELCOME_TEXT, reply_markup=main_menu_keyboard())
