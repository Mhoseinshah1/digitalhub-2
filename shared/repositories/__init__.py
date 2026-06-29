"""Data-access layer.

A repository is the only place that builds queries for its aggregate. It
receives an :class:`~sqlalchemy.ext.asyncio.AsyncSession`; it never creates
its own engine/session and never contains business decisions.
"""

from shared.repositories.user import UserRepository

__all__ = ["UserRepository"]
