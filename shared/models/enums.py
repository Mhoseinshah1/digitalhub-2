"""Enumerations used across the data model.

Stored as strings in the database (see ``SAEnum(..., native_enum=False)`` in
the models). Values are the canonical English identifiers.
"""

from __future__ import annotations

import enum


class UserRole(str, enum.Enum):
    """Role of a Telegram user inside the system."""

    USER = "user"
    ADMIN = "admin"


class ProductType(str, enum.Enum):
    """Kind of product on sale."""

    APPLE_ID = "apple_id"
    VPN = "vpn"


class OrderStatus(str, enum.Enum):
    """Lifecycle of an order."""

    PENDING = "pending"
    WAITING_RECEIPT = "waiting_receipt"
    APPROVED = "approved"
    REJECTED = "rejected"
    DELIVERED = "delivered"
    FAILED = "failed"


class TransactionType(str, enum.Enum):
    """Direction of a wallet ledger entry."""

    CREDIT = "credit"
    DEBIT = "debit"


class PaymentMethod(str, enum.Enum):
    """Payment gateway / method used."""

    CARD = "card"
    ZARINPAL = "zarinpal"


class PaymentStatus(str, enum.Enum):
    """Lifecycle of a payment."""

    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"


class DiscountType(str, enum.Enum):
    """How a discount value is applied."""

    PERCENT = "percent"
    FIXED = "fixed"


class TicketStatus(str, enum.Enum):
    """Lifecycle of a support ticket."""

    OPEN = "open"
    ANSWERED = "answered"
    CLOSED = "closed"
