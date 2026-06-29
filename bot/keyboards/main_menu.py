"""Main menu keyboard.

Phase 1: a minimal reply keyboard. Buttons are Persian and currently inert;
their handlers arrive in later phases.
"""

from __future__ import annotations

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

# Persian button labels (locale-ready).
BTN_APPLE_ID = "🍎 اپل آیدی"
BTN_VPN = "🌐 وی‌پی‌ان"
BTN_WALLET = "💰 کیف پول"
BTN_SUPPORT = "🎧 پشتیبانی"


def main_menu_keyboard() -> ReplyKeyboardMarkup:
    """Build the main menu reply keyboard."""
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BTN_APPLE_ID), KeyboardButton(text=BTN_VPN)],
            [KeyboardButton(text=BTN_WALLET), KeyboardButton(text=BTN_SUPPORT)],
        ],
        resize_keyboard=True,
    )
