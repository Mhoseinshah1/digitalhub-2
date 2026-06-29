"""Async SQLAlchemy engine and session factory.

Repositories receive an :class:`AsyncSession`; they never construct their own
engine. The declarative ``Base`` lives here and is imported by every model.
"""

from __future__ import annotations

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase

from shared.config import settings


class Base(DeclarativeBase):
    """Declarative base shared by all ORM models."""


def _make_engine() -> AsyncEngine:
    """Create the async engine from the configured DATABASE_URL."""
    kwargs: dict = {"echo": False, "future": True}
    if settings.is_sqlite:
        # SQLite (dev/tests) does not support real connection pooling args.
        kwargs["connect_args"] = {"check_same_thread": False}
    else:
        kwargs["pool_pre_ping"] = True
    return create_async_engine(settings.DATABASE_URL, **kwargs)


engine: AsyncEngine = _make_engine()

# Session factory. ``expire_on_commit=False`` so objects stay usable after
# commit (handlers/templates may read attributes afterwards).
async_session_factory: async_sessionmaker[AsyncSession] = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


@asynccontextmanager
async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield a session and commit/rollback around the block.

    Usage::

        async with get_session() as session:
            ...
    """
    session = async_session_factory()
    try:
        yield session
        await session.commit()
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


async def session_dependency() -> AsyncIterator[AsyncSession]:
    """FastAPI dependency that yields a session (no auto-commit).

    Routers/services decide when to commit; rollback happens on error.
    """
    session = async_session_factory()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()
