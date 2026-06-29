"""Logging setup for the bot process."""

from __future__ import annotations

import logging


def setup_logging(level: int = logging.INFO) -> None:
    """Configure root logging with a concise, timestamped format."""
    logging.basicConfig(
        level=level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    # aiogram is chatty at DEBUG; keep it at INFO unless globally raised.
    logging.getLogger("aiogram.event").setLevel(max(level, logging.INFO))
