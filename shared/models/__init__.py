"""ORM models package.

Importing this package registers every model on ``Base.metadata`` so Alembic
autogenerate and ``create_all`` see the full schema.
"""

from __future__ import annotations

from shared.database import Base
from shared.models.catalog import AppleIdStock, Plan, Product, Server
from shared.models.enums import (
    DiscountType,
    OrderStatus,
    PaymentMethod,
    PaymentStatus,
    ProductType,
    TicketStatus,
    TransactionType,
    UserRole,
)
from shared.models.order import Order, Payment, Transaction, VpnAccount
from shared.models.support import Discount, Setting, Ticket
from shared.models.user import User

__all__ = [
    "Base",
    # core
    "User",
    "Product",
    "Plan",
    "Server",
    "AppleIdStock",
    "Order",
    "Transaction",
    "Payment",
    "VpnAccount",
    "Discount",
    "Ticket",
    "Setting",
    # enums
    "UserRole",
    "ProductType",
    "OrderStatus",
    "TransactionType",
    "PaymentMethod",
    "PaymentStatus",
    "DiscountType",
    "TicketStatus",
]
