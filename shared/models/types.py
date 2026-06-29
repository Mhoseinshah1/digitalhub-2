"""Reusable column type helpers."""

from __future__ import annotations

import enum

from sqlalchemy import Enum as SAEnum


def str_enum(enum_cls: type[enum.Enum], length: int) -> SAEnum:
    """Build a non-native (VARCHAR) Enum that stores the member *value*.

    By default SQLAlchemy persists the enum member *name*. We store the
    lowercase ``.value`` instead so the data matches the lowercase
    ``server_default`` values used in the migrations and reads cleanly.
    """
    return SAEnum(
        enum_cls,
        native_enum=False,
        length=length,
        values_callable=lambda cls: [member.value for member in cls],
        validate_strings=True,
    )
