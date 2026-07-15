"""Add ownership and attempt integrity indexes.

Revision ID: 005
Revises: 004
"""
from alembic import op
import sqlalchemy as sa

revision = "005"
down_revision = "004"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_index("ix_progress_user_subject", "user_progress", ["user_id", "subject_id"], unique=True)
    op.create_index("ix_quiz_attempt_user_quiz", "quiz_attempts", ["user_id", "quiz_id"])
    op.create_index("ix_exam_result_user_exam_status", "exam_results", ["user_id", "exam_id", "status"])
    op.create_index("ix_exam_answer_result", "exam_answers", ["result_id"])
    op.create_index("ix_credit_transaction_user_created", "credit_transactions", ["user_id", "created_at"])
    op.create_index("ix_uploaded_file_user_created", "uploaded_files", ["user_id", "created_at"])


def downgrade() -> None:
    for name, table in [("ix_uploaded_file_user_created", "uploaded_files"), ("ix_credit_transaction_user_created", "credit_transactions"), ("ix_exam_answer_result", "exam_answers"), ("ix_exam_result_user_exam_status", "exam_results"), ("ix_quiz_attempt_user_quiz", "quiz_attempts"), ("ix_progress_user_subject", "user_progress")]:
        op.drop_index(name, table_name=table)
