"""User model.

NOTE: ``balance`` is a cached projection of the transaction ledger. It must
ONLY be written by the wallet service inside the same DB transaction that
inserts a ``transaction`` row recording ``balance_after``. Never mutate it
directly from a handler/router.
"""

from __future__ import annotations

from typing import TYPE_CHECKING

from sqlalchemy import BigInteger, Boolean, Numeric, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database import Base
from shared.models.enums import UserRole
from shared.models.mixins import TimestampMixin
from shared.models.types import str_enum

if TYPE_CHECKING:
    from shared.models.order import Order, Payment, Transaction
    from shared.models.support import Ticket


class User(TimestampMixin, Base):
    """A Telegram user known to the bot."""

    __tablename__ = "user"

    id: Mapped[int] = mapped_column(primary_key=True)
    telegram_id: Mapped[int] = mapped_column(
        BigInteger, unique=True, index=True, nullable=False
    )
    username: Mapped[str | None] = mapped_column(String(64), nullable=True)
    full_name: Mapped[str | None] = mapped_column(String(255), nullable=True)

    role: Mapped[UserRole] = mapped_column(
        str_enum(UserRole, 16),
        default=UserRole.USER,
        nullable=False,
    )

    # Cached wallet balance in Toman. Source of truth is the ledger.
    balance: Mapped[int] = mapped_column(
        Numeric(18, 0), default=0, nullable=False
    )

    is_blocked: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False
    )

    # --- relationships -------------------------------------------------------
    orders: Mapped[list["Order"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="user",
        cascade="all, delete-orphan",
        foreign_keys="Payment.user_id",
    )
    tickets: Mapped[list["Ticket"]] = relationship(
        back_populates="user", cascade="all, delete-orphan"
    )

    def __repr__(self) -> str:  # pragma: no cover - debug helper
        return f"<User id={self.id} tg={self.telegram_id} role={self.role}>"
