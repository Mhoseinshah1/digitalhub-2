"""x-ui panel client interface.

Phase 1: CONTRACT ONLY. No HTTP calls are implemented. The real multi-server
client lands in Phase 4 and must satisfy this interface so callers do not
change.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class XuiClientConfig:
    """Connection settings for a single x-ui server."""

    panel_url: str
    username: str
    password: str
    inbound_id: int | None = None


@dataclass(slots=True)
class XuiAccount:
    """Result of provisioning a client on an x-ui inbound."""

    uuid: str
    sub_link: str
    expire_at: datetime | None
    traffic_total_bytes: int


class XuiClient(ABC):
    """Abstract x-ui panel client.

    A concrete implementation is provided in Phase 4. Until then this exists so
    services can be typed against a stable contract.
    """

    def __init__(self, config: XuiClientConfig) -> None:
        self.config = config

    @abstractmethod
    async def login(self) -> None:
        """Authenticate against the panel."""
        raise NotImplementedError

    @abstractmethod
    async def create_account(
        self, *, email: str, traffic_gb: int, duration_days: int
    ) -> XuiAccount:
        """Create a client on the configured inbound."""
        raise NotImplementedError

    @abstractmethod
    async def delete_account(self, uuid: str) -> None:
        """Remove a client by uuid."""
        raise NotImplementedError

    @abstractmethod
    async def get_usage(self, uuid: str) -> int:
        """Return used traffic in bytes for a client."""
        raise NotImplementedError
