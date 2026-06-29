"""User repository."""

from __future__ import annotations

from sqlalchemy import select

from shared.models.user import User
from shared.repositories.base import BaseRepository


class UserRepository(BaseRepository[User]):
    """Data access for :class:`~shared.models.user.User`."""

    model = User

    async def get_by_telegram_id(self, telegram_id: int) -> User | None:
        """Return the user with the given Telegram id, or ``None``."""
        stmt = select(User).where(User.telegram_id == telegram_id)
        return await self.session.scalar(stmt)
