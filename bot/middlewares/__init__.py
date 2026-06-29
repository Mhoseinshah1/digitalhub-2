"""aiogram middlewares.

Phase 1 ships empty stubs for auth and throttling so the wiring exists and
later phases can fill in behaviour without restructuring.
"""

from bot.middlewares.auth import AuthMiddleware
from bot.middlewares.throttling import ThrottlingMiddleware

__all__ = ["AuthMiddleware", "ThrottlingMiddleware"]
