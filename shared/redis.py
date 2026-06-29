"""Async Redis client.

Used for aiogram FSM storage, distributed locks and throttling. A single
shared client is created lazily and reused process-wide.
"""

from __future__ import annotations

from redis.asyncio import Redis, from_url

from shared.config import settings

_client: Redis | None = None


def get_redis() -> Redis:
    """Return the shared async Redis client, creating it on first use."""
    global _client
    if _client is None:
        _client = from_url(
            settings.REDIS_URL,
            encoding="utf-8",
            decode_responses=True,
        )
    return _client


async def close_redis() -> None:
    """Close the shared Redis client (call on application shutdown)."""
    global _client
    if _client is not None:
        await _client.aclose()
        _client = None
