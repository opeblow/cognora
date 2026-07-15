"""Fix payment column types: amount and credits_purchased from String to Integer

Revision ID: 004
Revises: 003
Create Date: 2026-07-08

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite


revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _is_sqlite() -> bool:
    return op.get_context().dialect.name == "sqlite"


def upgrade() -> None:
    if _is_sqlite():
        with op.batch_alter_table("payments") as batch_op:
            batch_op.alter_column(
                "amount",
                type_=sa.Integer(),
                existing_type=sa.String(50),
                postgresql_using="amount::integer",
            )
            batch_op.alter_column(
                "credits_purchased",
                type_=sa.Integer(),
                existing_type=sa.String(50),
                postgresql_using="credits_purchased::integer",
            )
    else:
        op.execute(
            "ALTER TABLE payments ALTER COLUMN amount TYPE integer USING amount::integer"
        )
        op.execute(
            "ALTER TABLE payments ALTER COLUMN credits_purchased TYPE integer USING credits_purchased::integer"
        )
        op.execute(
            "ALTER TABLE payments ALTER COLUMN amount SET NOT NULL"
        )


def downgrade() -> None:
    if _is_sqlite():
        with op.batch_alter_table("payments") as batch_op:
            batch_op.alter_column(
                "amount",
                type_=sa.String(50),
                existing_type=sa.Integer(),
            )
            batch_op.alter_column(
                "credits_purchased",
                type_=sa.String(50),
                existing_type=sa.Integer(),
            )
    else:
        op.execute(
            "ALTER TABLE payments ALTER COLUMN amount TYPE varchar(50) USING amount::text"
        )
        op.execute(
            "ALTER TABLE payments ALTER COLUMN credits_purchased TYPE varchar(50) USING credits_purchased::text"
        )
        op.execute(
            "ALTER TABLE payments ALTER COLUMN amount SET NOT NULL"
        )
