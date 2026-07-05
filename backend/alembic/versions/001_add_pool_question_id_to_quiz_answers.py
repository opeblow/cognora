"""Add pool_question_id to quiz_answers

Revision ID: 001
Revises:
Create Date: 2026-06-30

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "quiz_answers",
        sa.Column(
            "pool_question_id",
            sa.String(),
            sa.ForeignKey("question_pool.id", ondelete="CASCADE"),
            nullable=True,
        ),
    )
    op.alter_column("quiz_answers", "question_id", nullable=True)


def downgrade() -> None:
    op.alter_column("quiz_answers", "question_id", nullable=False)
    op.drop_column("quiz_answers", "pool_question_id")
