"""Payment gateway integrations (interface only in Phase 1)."""

from integrations.gateways.base import PaymentGateway, PaymentResult

__all__ = ["PaymentGateway", "PaymentResult"]
