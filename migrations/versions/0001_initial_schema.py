"""initial schema (full Phase 1 data model)

Revision ID: 0001_initial
Revises:
Create Date: 2026-06-29

Creates the entire database schema up front so later phases avoid costly
structural migrations. Enum-typed columns are stored as VARCHAR (matching the
``native_enum=False`` ORM definitions).
"""
from __future__ import annotations

from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "0001_initial"
down_revision: str | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def _timestamps() -> list[sa.Column]:
    return [
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    ]


def upgrade() -> None:
    # --- user ----------------------------------------------------------------
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("telegram_id", sa.BigInteger(), nullable=False),
        sa.Column("username", sa.String(length=64), nullable=True),
        sa.Column("full_name", sa.String(length=255), nullable=True),
        sa.Column(
            "role",
            sa.String(length=16),
            server_default="user",
            nullable=False,
        ),
        sa.Column(
            "balance",
            sa.Numeric(precision=18, scale=0),
            server_default="0",
            nullable=False,
        ),
        sa.Column(
            "is_blocked",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        *_timestamps(),
    )
    op.create_index(
        "ix_user_telegram_id", "user", ["telegram_id"], unique=True
    )

    # --- product -------------------------------------------------------------
    op.create_table(
        "product",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        *_timestamps(),
    )

    # --- server --------------------------------------------------------------
    op.create_table(
        "server",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("panel_url", sa.String(length=512), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=False),
        sa.Column("password", sa.String(length=512), nullable=False),
        sa.Column("inbound_id", sa.Integer(), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        *_timestamps(),
    )

    # --- plan ----------------------------------------------------------------
    op.create_table(
        "plan",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("duration_days", sa.Integer(), nullable=False),
        sa.Column("traffic_gb", sa.Integer(), nullable=False),
        sa.Column("price", sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["product_id"], ["product.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["server_id"], ["server.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_plan_product_id", "plan", ["product_id"])
    op.create_index("ix_plan_server_id", "plan", ["server_id"])

    # --- order ---------------------------------------------------------------
    op.create_table(
        "order",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("plan_id", sa.Integer(), nullable=True),
        sa.Column(
            "status",
            sa.String(length=20),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("amount", sa.Numeric(precision=18, scale=0), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["product_id"], ["product.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["plan_id"], ["plan.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_order_user_id", "order", ["user_id"])
    op.create_index("ix_order_product_id", "order", ["product_id"])
    op.create_index("ix_order_plan_id", "order", ["plan_id"])
    op.create_index("ix_order_status", "order", ["status"])

    # --- apple_id_stock ------------------------------------------------------
    op.create_table(
        "apple_id_stock",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("product_id", sa.Integer(), nullable=True),
        sa.Column("credentials", sa.Text(), nullable=False),
        sa.Column(
            "is_sold",
            sa.Boolean(),
            server_default=sa.false(),
            nullable=False,
        ),
        sa.Column("order_id", sa.Integer(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["product_id"], ["product.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["order.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "ix_apple_id_stock_product_id", "apple_id_stock", ["product_id"]
    )
    op.create_index("ix_apple_id_stock_is_sold", "apple_id_stock", ["is_sold"])
    op.create_index(
        "ix_apple_id_stock_order_id", "apple_id_stock", ["order_id"]
    )

    # --- transaction ---------------------------------------------------------
    op.create_table(
        "transaction",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column(
            "balance_after",
            sa.Numeric(precision=18, scale=0),
            nullable=False,
        ),
        sa.Column("reason", sa.String(length=255), nullable=True),
        sa.Column("ref", sa.String(length=255), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["order.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_transaction_user_id", "transaction", ["user_id"])
    op.create_index("ix_transaction_order_id", "transaction", ["order_id"])

    # --- payment -------------------------------------------------------------
    op.create_table(
        "payment",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("order_id", sa.Integer(), nullable=True),
        sa.Column("method", sa.String(length=16), nullable=False),
        sa.Column("amount", sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            server_default="pending",
            nullable=False,
        ),
        sa.Column("receipt_file_id", sa.String(length=255), nullable=True),
        sa.Column("ref", sa.String(length=255), nullable=True),
        sa.Column("approved_by", sa.Integer(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["order_id"], ["order.id"], ondelete="SET NULL"
        ),
        sa.ForeignKeyConstraint(
            ["approved_by"], ["user.id"], ondelete="SET NULL"
        ),
    )
    op.create_index("ix_payment_user_id", "payment", ["user_id"])
    op.create_index("ix_payment_order_id", "payment", ["order_id"])
    op.create_index("ix_payment_status", "payment", ["status"])

    # --- vpn_account ---------------------------------------------------------
    op.create_table(
        "vpn_account",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("order_id", sa.Integer(), nullable=False),
        sa.Column("server_id", sa.Integer(), nullable=True),
        sa.Column("sub_link", sa.Text(), nullable=True),
        sa.Column("uuid", sa.String(length=64), nullable=True),
        sa.Column("expire_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "traffic_used",
            sa.BigInteger(),
            server_default="0",
            nullable=False,
        ),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["order_id"], ["order.id"], ondelete="CASCADE"
        ),
        sa.ForeignKeyConstraint(
            ["server_id"], ["server.id"], ondelete="SET NULL"
        ),
    )
    op.create_index(
        "ix_vpn_account_order_id", "vpn_account", ["order_id"], unique=True
    )
    op.create_index("ix_vpn_account_server_id", "vpn_account", ["server_id"])
    op.create_index("ix_vpn_account_uuid", "vpn_account", ["uuid"])

    # --- discount ------------------------------------------------------------
    op.create_table(
        "discount",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("type", sa.String(length=16), nullable=False),
        sa.Column("value", sa.Numeric(precision=18, scale=0), nullable=False),
        sa.Column("max_uses", sa.Integer(), nullable=True),
        sa.Column(
            "used_count",
            sa.Integer(),
            server_default="0",
            nullable=False,
        ),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column(
            "is_active",
            sa.Boolean(),
            server_default=sa.true(),
            nullable=False,
        ),
        *_timestamps(),
    )
    op.create_index("ix_discount_code", "discount", ["code"], unique=True)

    # --- ticket --------------------------------------------------------------
    op.create_table(
        "ticket",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("subject", sa.String(length=255), nullable=False),
        sa.Column("message", sa.Text(), nullable=False),
        sa.Column(
            "status",
            sa.String(length=16),
            server_default="open",
            nullable=False,
        ),
        *_timestamps(),
        sa.ForeignKeyConstraint(
            ["user_id"], ["user.id"], ondelete="CASCADE"
        ),
    )
    op.create_index("ix_ticket_user_id", "ticket", ["user_id"])
    op.create_index("ix_ticket_status", "ticket", ["status"])

    # --- setting -------------------------------------------------------------
    op.create_table(
        "setting",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("key", sa.String(length=128), nullable=False),
        sa.Column("value", sa.Text(), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        *_timestamps(),
    )
    op.create_index("ix_setting_key", "setting", ["key"], unique=True)


def downgrade() -> None:
    op.drop_table("setting")
    op.drop_table("ticket")
    op.drop_table("discount")
    op.drop_table("vpn_account")
    op.drop_table("payment")
    op.drop_table("transaction")
    op.drop_table("apple_id_stock")
    op.drop_table("order")
    op.drop_table("plan")
    op.drop_table("server")
    op.drop_table("product")
    op.drop_table("user")
