"""Catalog & inventory models: product, plan, server, apple_id_stock."""

from __future__ import annotations

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
from shared.models.enums import ProductType
from shared.models.mixins import TimestampMixin
from shared.models.types import str_enum

if TYPE_CHECKING:
    from shared.models.order import Order, VpnAccount


class Product(TimestampMixin, Base):
    """A sellable product (an Apple ID family or a VPN family)."""

    __tablename__ = "product"

    id: Mapped[int] = mapped_column(primary_key=True)
    type: Mapped[ProductType] = mapped_column(
        str_enum(ProductType, 16), nullable=False
    )
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # --- relationships -------------------------------------------------------
    plans: Mapped[list["Plan"]] = relationship(
        back_populates="product", cascade="all, delete-orphan"
    )
    orders: Mapped[list["Order"]] = relationship(back_populates="product")


class Server(TimestampMixin, Base):
    """An x-ui panel server (multi-server support)."""

    __tablename__ = "server"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    panel_url: Mapped[str] = mapped_column(String(512), nullable=False)
    username: Mapped[str] = mapped_column(String(255), nullable=False)
    # NOTE: x-ui panel password. Stored for server automation; treat as secret.
    password: Mapped[str] = mapped_column(String(512), nullable=False)
    inbound_id: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # --- relationships -------------------------------------------------------
    plans: Mapped[list["Plan"]] = relationship(back_populates="server")
    vpn_accounts: Mapped[list["VpnAccount"]] = relationship(
        back_populates="server"
    )


class Plan(TimestampMixin, Base):
    """A VPN-specific plan attached to a product and a server."""

    __tablename__ = "plan"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int] = mapped_column(
        ForeignKey("product.id", ondelete="CASCADE"), nullable=False, index=True
    )
    server_id: Mapped[int | None] = mapped_column(
        ForeignKey("server.id", ondelete="SET NULL"), nullable=True, index=True
    )

    title: Mapped[str] = mapped_column(String(255), nullable=False)
    duration_days: Mapped[int] = mapped_column(Integer, nullable=False)
    traffic_gb: Mapped[int] = mapped_column(Integer, nullable=False)
    # Price in Toman.
    price: Mapped[int] = mapped_column(Numeric(18, 0), nullable=False)
    is_active: Mapped[bool] = mapped_column(
        Boolean, default=True, nullable=False
    )

    # --- relationships -------------------------------------------------------
    product: Mapped["Product"] = relationship(back_populates="plans")
    server: Mapped["Server | None"] = relationship(back_populates="plans")
    orders: Mapped[list["Order"]] = relationship(back_populates="plan")


class AppleIdStock(TimestampMixin, Base):
    """A single Apple ID inventory item (credentials)."""

    __tablename__ = "apple_id_stock"

    id: Mapped[int] = mapped_column(primary_key=True)
    product_id: Mapped[int | None] = mapped_column(
        ForeignKey("product.id", ondelete="SET NULL"), nullable=True, index=True
    )
    # Stored credentials blob (email/password/notes). Treat as secret.
    credentials: Mapped[str] = mapped_column(Text, nullable=False)

    is_sold: Mapped[bool] = mapped_column(
        Boolean, default=False, nullable=False, index=True
    )
    order_id: Mapped[int | None] = mapped_column(
        ForeignKey("order.id", ondelete="SET NULL"), nullable=True, index=True
    )

    # --- relationships -------------------------------------------------------
    order: Mapped["Order | None"] = relationship(back_populates="apple_id_item")
