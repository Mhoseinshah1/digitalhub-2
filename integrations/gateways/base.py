"""Payment gateway contract.

Phase 1: CONTRACT ONLY. Concrete gateways (card-to-card, Zarinpal) are
implemented in Phase 2 and must satisfy this interface.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(slots=True)
class PaymentResult:
    """Outcome of starting/verifying a payment."""

    success: bool
    ref: str | None = None
    pay_url: str | None = None
    message: str | None = None


class PaymentGateway(ABC):
    """Abstract payment gateway."""

    name: str

    @abstractmethod
    async def request(self, *, amount: int, order_id: int) -> PaymentResult:
        """Start a payment for ``amount`` (Toman) tied to ``order_id``."""
        raise NotImplementedError

    @abstractmethod
    async def verify(self, *, ref: str, amount: int) -> PaymentResult:
        """Verify a previously requested payment by reference."""
        raise NotImplementedError
