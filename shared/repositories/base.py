"""Generic async repository base."""

from __future__ import annotations

from typing import Generic, TypeVar

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from shared.database import Base

ModelT = TypeVar("ModelT", bound=Base)


class BaseRepository(Generic[ModelT]):
    """Common CRUD primitives shared by concrete repositories."""

    model: type[ModelT]

    def __init__(self, session: AsyncSession) -> None:
        self.session = session

    async def get(self, obj_id: int) -> ModelT | None:
        """Return a row by primary key, or ``None``."""
        return await self.session.get(self.model, obj_id)

    async def list(self, limit: int = 100, offset: int = 0) -> list[ModelT]:
        """Return a page of rows ordered by primary key."""
        stmt = (
            select(self.model)
            .order_by(self.model.id)  # type: ignore[attr-defined]
            .limit(limit)
            .offset(offset)
        )
        result = await self.session.scalars(stmt)
        return list(result.all())

    async def add(self, obj: ModelT) -> ModelT:
        """Stage a new row and flush so it gets a primary key."""
        self.session.add(obj)
        await self.session.flush()
        return obj
