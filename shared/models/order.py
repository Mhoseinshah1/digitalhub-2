"""Order, transaction (wallet ledger), payment and vpn_account models."""

from __future__ import annotations

from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    Numeric,
    String,
    Text,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from shared.database import Base
from shared.models.enums import (
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    TransactionType,
)
from shared.models.mixins import TimestampMixin
from shared.models.types import str_enum

if TYPE_CHECKING:
    from shared.models.catalog import AppleIdStock, Plan, Product, Server
    from shared.models.user import User


class Order(TimestampMixin, Base):
    """A purchase order for a product (Apple ID or VPN plan)."""

    __tablename__ = "order"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("product.id", ondelete="SET NULL"), nullable=True, index=True
    )
    plan_id: Mapped[int | None] = mapped_column(
        ForeignKey("plan.id", ondelete="SET NULL"), nullable=True, index=True
    )

    status: Mapped[OrderStatus] = mapped_column(
        str_enum(OrderStatus, 20),
        default=OrderStatus.PENDING,
        nullable=False,
        index=True,
    )
    # Final charged amount in Toman.
    amount: Mapped[int] = mapped_column(Numeric(18, 0), nullable=False)

    # --- relationships -------------------------------------------------------
    user: Mapped["User"] = relationship(back_populates="orders")
    product: Mapped["Product | None"] = relationship(back_populates="orders")
    plan: Mapped["Plan | None"] = relationship(back_populates="orders")
    payments: Mapped[list["Payment"]] = relationship(
        back_populates="order", cascade="all, delete-orphan"
    )
    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="order"
    )
    apple_id_item: Mapped["AppleIdStock | None"] = relationship(
        back_populates="order", uselist=False
    )
    vpn_account: Mapped["VpnAccount | None"] = relationship(
        back_populates="order", uselist=False, cascade="all, delete-orphan"
    )


class Transaction(TimestampMixin, Base):
    """Immutable wallet ledger entry.

    Every wallet movement is one row here. ``balance_after`` is the user's
    balance immediately after applying this entry, written atomically with the
    update to ``user.balance``.
    """

    __tablename__ = "transaction"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("order.id", ondelete="SET NULL"), nullable=True, index=True
    )

    type: Mapped[TransactionType] = mapped_column(
        str_enum(TransactionType, 16), nullable=False
    )
    # Positive magnitude in Toman; direction is given by ``type``.
    amount: Mapped[int] = mapped_column(Numeric(18, 0), nullable=False)
    balance_after: Mapped[int] = mapped_column(Numeric(18, 0), nullable=False)

    # Human-readable reason (Persian) and a machine reference (e.g. payment id).
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)
    ref: Mapped[str | None] = mapped_column(String(255), nullable=True)

    # --- relationships -------------------------------------------------------
    user: Mapped["User"] = relationship(back_populates="transactions")
    order: Mapped["Order | None"] = relationship(back_populates="transactions")


class Payment(TimestampMixin, Base):
    """A payment attempt via a gateway (card or Zarinpal)."""

    __tablename__ = "payment"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("user.id", ondelete="CASCADE"), nullable=False, index=True
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("order.id", ondelete="SET NULL"), nullable=True, index=True
    )

    method: Mapped[PaymentMethod] = mapped_column(
        str_enum(PaymentMethod, 16), nullable=False
    )
    amount: Mapped[int] = mapped_column(Numeric(18, 0), nullable=False)
    status: Mapped[PaymentStatus] = mapped_column(
        str_enum(PaymentStatus, 16),
        default=PaymentStatus.PENDING,
        nullable=False,
        index=True,
    )

    # Telegram file id of an uploaded card-to-card receipt photo.
    receipt_file_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Gateway transaction reference / authority.
    ref: Mapped[str | None] = mapped_column(String(255), nullable=True)
    # Admin (user id) who approved/rejected a card payment.
    approved_by: Mapped[int | None] = mapped_column(
        ForeignKey("user.id", ondelete="SET NULL"), nullable=True
    )

    # --- relationships -------------------------------------------------------
    user: Mapped["User"] = relationship(
        back_populates="payments", foreign_keys=[user_id]
    )
    order: Mapped["Order | None"] = relationship(back_populates="payments")


class VpnAccount(TimestampMixin, Base):
    """A provisioned VPN account tied to an order and an x-ui server."""

    __tablename__ = "vpn_account"

    id: Mapped[int] = mapped_column(primary_key=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("order.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
        index=True,
    )
    server_id: Mapped[int | None] = mapped_column(
        ForeignKey("server.id", ondelete="SET NULL"), nullable=True, index=True
    )

    sub_link: Mapped[str | None] = mapped_column(Text, nullable=True)
    uuid: Mapped[str | None] = mapped_column(String(64), nullable=True, index=True)
    expire_at: Mapped[datetime | None] = mapped_column(nullable=True)
    # Traffic used in bytes (synced from x-ui in later phases).
    traffic_used: Mapped[int] = mapped_column(
        BigInteger, default=0, nullable=False
    )

    # --- relationships -------------------------------------------------------
    order: Mapped["Order"] = relationship(back_populates="vpn_account")
    server: Mapped["Server | None"] = relationship(
        back_populates="vpn_accounts"
    )
