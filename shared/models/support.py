"""Auxiliary models: discount, ticket, setting."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    Boolean,
    ForeignKey,
    Integer,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database import Base
from shared.models.enums import DiscountType, TicketStatus
from shared.models.mixins import TimestampMixin
from shared.models.types import str_enum

if TYPE_CHECKING:
    from shared.models.user import User


class Discount(TimestampMixin, Base):
    """A discount / coupon code."""

    __tablename__ = "discount"

    id: Mapped[int] = mapped_column(primary_key=True)
    code: Mapped[str] = mapped_column(
        String(64), unique=True, index=True, nullable=False
    )
    type: Mapped[DiscountType] = mapped_column(
        str_enum(DiscountType, 16), nullable=False
    )
    # Percent (0-100) or fixed amount in Toman, per ``type``.
    value: Mapped[int] = mapped_column(Numeric(18, 0), nullable=False)

    max_uses: Mapped[int | None] = mapped_column(Integer, nullable=True)
    used_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    expires_at: Mapped[datetime | None] = mapped_column(nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )


class Ticket(TimestampMixin, Base):
    """A support ticket opened by a user."""

    __tablename__ = "ticket"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    subject: Mapped[str] = mapped_column(String(255), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[TicketStatus] = mapped_column(
        str_enum(TicketStatus, 16),
        default=TicketStatus.OPEN,
        nullable=False,
        index=True,
    )

    # --- relationships -------------------------------------------------------
    user: Mapped["User"] = relationship(back_populates="tickets")


class Setting(TimestampMixin, Base):
    """A dynamic key/value setting (e.g. card number, support contact)."""

    __tablename__ = "setting"

    id: Mapped[int] = mapped_column(primary_key=True)
    key: Mapped[str] = mapped_column(
        String(128), unique=True, index=True, nullable=False
    )
    value: Mapped[str | None] = mapped_column(Text, nullable=True)
    description: Mapped[str | None] = mapped_column(String(255), nullable=True)
