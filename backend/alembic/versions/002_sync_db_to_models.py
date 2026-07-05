"""Sync database schema to match all SQLAlchemy models

Revision ID: 002
Revises: 001
Create Date: 2026-07-03

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "002"
down_revision: Union[str, None] = "001"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- Create tables with no FK dependencies first ----
    op.create_table(
        "rate_limit_audit",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True, index=True),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("endpoint", sa.String(200), nullable=False),
        sa.Column("method", sa.String(10), nullable=False),
        sa.Column("status_code", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "badges",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("icon", sa.String(500), nullable=True),
        sa.Column("criteria_type", sa.String(100), nullable=False),
        sa.Column("criteria_value", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "syllabi",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("exam_board", sa.String(20), nullable=False),
        sa.Column("subject", sa.String(200), nullable=False),
        sa.Column("year", sa.String(4), nullable=False),
        sa.Column("syllabus_data", sa.JSON(), nullable=False),
        sa.Column("source_url", sa.String(500), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("idx_syllabi_board_subject", "syllabi", ["exam_board", "subject"])

    # ---- Tables that FK to existing tables (subjects, users, topics) ----
    op.create_table(
        "chapters",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("subject_id", sa.String(), nullable=False, index=True),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("display_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("is_published", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "live_sessions",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("room_id", sa.String(255), nullable=False, unique=True, index=True),
        sa.Column("tutor_id", sa.String(), nullable=False),
        sa.Column("student_id", sa.String(), nullable=True),
        sa.Column("subject", sa.String(255), nullable=False),
        sa.Column("topic", sa.String(255), nullable=True),
        sa.Column("status", sa.String(50), nullable=True, server_default="pending"),
        sa.Column("provider", sa.String(50), nullable=True, server_default="mock"),
        sa.Column("provider_room_id", sa.String(500), nullable=True),
        sa.Column("recording_url", sa.String(1000), nullable=True),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["tutor_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["student_id"], ["users.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "study_lobbies",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("subject", sa.String(255), nullable=True),
        sa.Column("topic", sa.String(255), nullable=True),
        sa.Column("created_by", sa.String(), nullable=False),
        sa.Column("max_participants", sa.Integer(), nullable=True, server_default="10"),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["created_by"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "content_issues",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column("content_type", sa.String(20), nullable=False),
        sa.Column("content_id", sa.String(), nullable=False),
        sa.Column("section_index", sa.Integer(), nullable=True),
        sa.Column("severity", sa.String(20), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("status", sa.String(20), nullable=False, server_default="open"),
        sa.Column("ai_response", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("resolved_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "uploaded_files",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("original_filename", sa.String(500), nullable=False),
        sa.Column("stored_filename", sa.String(500), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("file_size", sa.Integer(), nullable=False),
        sa.Column("storage_path", sa.String(1000), nullable=False),
        sa.Column("storage_backend", sa.String(50), nullable=True, server_default="local"),
        sa.Column("ocr_text", sa.Text(), nullable=True),
        sa.Column("ocr_status", sa.String(50), nullable=True, server_default="pending"),
        sa.Column("ocr_processed_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "audio_recordings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("file_path", sa.String(1000), nullable=False),
        sa.Column("mime_type", sa.String(100), nullable=False),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("transcript", sa.Text(), nullable=True),
        sa.Column("ai_feedback", sa.Text(), nullable=True),
        sa.Column("processing_status", sa.String(50), nullable=True, server_default="pending"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_settings",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False, unique=True),
        sa.Column("study_reminder_enabled", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("study_reminder_time", sa.String(5), nullable=True, server_default="09:00"),
        sa.Column("quiz_reminder_enabled", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("email_notifications", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("exam_focus", sa.String(50), nullable=True, server_default="JAMB"),
        sa.Column("preferred_subjects", sa.JSON(), nullable=True),
        sa.Column("difficulty_preference", sa.String(20), nullable=True, server_default="medium"),
        sa.Column("timezone", sa.String(50), nullable=True, server_default="Africa/Lagos"),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "flashcards",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("subject_id", sa.String(), nullable=True),
        sa.Column("topic_id", sa.String(), nullable=True),
        sa.Column("section_index", sa.Integer(), nullable=True),
        sa.Column("question", sa.Text(), nullable=False),
        sa.Column("answer", sa.Text(), nullable=False),
        sa.Column("difficulty", sa.String(50), nullable=True, server_default="medium"),
        sa.Column("tags", sa.Text(), nullable=True),
        sa.Column("source", sa.String(100), nullable=True, server_default="ai_generated"),
        sa.Column("is_active", sa.Boolean(), nullable=True, server_default="true"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["subject_id"], ["subjects.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "textbook_sections",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("topic_id", sa.String(), nullable=False, index=True),
        sa.Column("title", sa.String(300), nullable=False),
        sa.Column("content", sa.Text(), nullable=True),
        sa.Column("section_index", sa.Integer(), nullable=False),
        sa.Column("word_count", sa.Integer(), nullable=True),
        sa.Column("is_generated", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("generated_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["topic_id"], ["topics.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ---- Tables that FK to tables created above ----
    op.create_table(
        "live_session_participants",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False, index=True),
        sa.Column("user_id", sa.String(), nullable=False, index=True),
        sa.Column("role", sa.String(10), nullable=False, server_default="audience"),
        sa.Column("joined_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("left_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["session_id"], ["live_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "classroom_messages",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("session_id", sa.String(), nullable=False, index=True),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("message_type", sa.String(20), nullable=False, server_default="chat"),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["session_id"], ["live_sessions.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "lobby_messages",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("lobby_id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=True),
        sa.Column("username", sa.String(255), nullable=True),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("is_ai_response", sa.Boolean(), nullable=True, server_default="false"),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["lobby_id"], ["study_lobbies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user_badges",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("user_id", sa.String(), nullable=False),
        sa.Column("badge_id", sa.String(), nullable=False),
        sa.Column("awarded_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["badge_id"], ["badges.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "flashcard_reviews",
        sa.Column("id", sa.String(), nullable=False),
        sa.Column("flashcard_id", sa.String(), nullable=False, unique=True),
        sa.Column("ease_factor", sa.Float(), nullable=True, server_default="2.5"),
        sa.Column("interval_days", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("repetitions", sa.Integer(), nullable=True, server_default="0"),
        sa.Column("next_review_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("last_reviewed_at", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["flashcard_id"], ["flashcards.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )

    # ---- Add missing columns to existing tables ----
    op.add_column("lessons", sa.Column("chapter_id", sa.String(), nullable=True, index=True))
    op.create_foreign_key(
        "lessons_chapter_id_fkey", "lessons", "chapters",
        ["chapter_id"], ["chapters.id"], ondelete="SET NULL",
    )

    # ---- Add missing user columns (idempotent - skip if already exist) ----
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS longest_streak INTEGER NOT NULL DEFAULT 0")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS streak_freezes INTEGER NOT NULL DEFAULT 0")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS total_xp INTEGER NOT NULL DEFAULT 0")
    op.execute("ALTER TABLE users ADD COLUMN IF NOT EXISTS level INTEGER NOT NULL DEFAULT 1")


def downgrade() -> None:
    op.drop_column("lessons", "chapter_id")
    op.drop_table("flashcard_reviews")
    op.drop_table("user_badges")
    op.drop_table("lobby_messages")
    op.drop_table("classroom_messages")
    op.drop_table("live_session_participants")
    op.drop_table("textbook_sections")
    op.drop_table("flashcards")
    op.drop_table("user_settings")
    op.drop_table("audio_recordings")
    op.drop_table("uploaded_files")
    op.drop_table("content_issues")
    op.drop_table("study_lobbies")
    op.drop_table("live_sessions")
    op.drop_table("chapters")
    op.drop_table("syllabi")
    op.drop_table("badges")
    op.drop_table("rate_limit_audit")
