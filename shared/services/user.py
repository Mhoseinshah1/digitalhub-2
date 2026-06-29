"""User service.

The only Phase 1 business operation: register-or-fetch a user on /start and
promote the configured main admin. Wallet mutations are intentionally NOT
implemented here yet (Phase 2) — when added, they must go through the
transaction ledger, never by writing ``user.balance`` directly.
"""

from __future__ import annotations

from sqlalchemy.ext.asyncio import AsyncSession

from shared.config import settings
from shared.models.enums import UserRole
from shared.models.user import User
from shared.repositories.user import UserRepository


class UserService:
    """Business logic for users."""

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self.users = UserRepository(session)

    async def get_or_create(
        self,
        telegram_id: int,
        *,
        username: str | None = None,
        full_name: str | None = None,
    ) -> User:
        """Return the existing user or create a new one.

        The configured ``MAIN_ADMIN_ID`` is always (re)assigned the admin role.
        """
        user = await self.users.get_by_telegram_id(telegram_id)
        if user is None:
            user = User(
                telegram_id=telegram_id,
                username=username,
                full_name=full_name,
                role=self._role_for(telegram_id),
            )
            await self.users.add(user)
            return user

        # Keep light profile fields and admin role in sync.
        if username is not None and user.username != username:
            user.username = username
        if full_name is not None and user.full_name != full_name:
            user.full_name = full_name
        if telegram_id == settings.MAIN_ADMIN_ID and user.role != UserRole.ADMIN:
            user.role = UserRole.ADMIN
        return user

    @staticmethod
    def _role_for(telegram_id: int) -> UserRole:
        """Decide the initial role for a telegram id."""
        if telegram_id == settings.MAIN_ADMIN_ID:
            return UserRole.ADMIN
        return UserRole.USER

    async def ensure_main_admin(self) -> User:
        """Ensure the configured main admin exists with the admin role.

        Used by install/bootstrap tooling.
        """
        return await self.get_or_create(settings.MAIN_ADMIN_ID)
