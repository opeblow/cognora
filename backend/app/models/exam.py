import uuid
from datetime import datetime, timezone
from sqlalchemy import Column, String, Text, Boolean, Integer, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.database.base import Base


class Exam(Base):
    __tablename__ = "exams"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    subject_id = Column(String, ForeignKey("subjects.id", ondelete="CASCADE"), nullable=False, index=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    exam_type = Column(String(50), nullable=False)
    year = Column(String(50), nullable=True)
    time_limit_minutes = Column(Integer, nullable=True)
    total_questions = Column(Integer, nullable=True)
    pass_percentage = Column(Integer, nullable=True)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    subject = relationship("Subject", back_populates="exams")
    questions = relationship("ExamQuestion", back_populates="exam", cascade="all, delete-orphan")
    results = relationship("ExamResult", back_populates="exam", cascade="all, delete-orphan")


class ExamQuestion(Base):
    __tablename__ = "exam_questions"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False, index=True)
    text = Column(Text, nullable=False)
    options = Column(JSON, nullable=False)
    correct_answer = Column(String(50), nullable=False)
    explanation = Column(Text, nullable=True)
    order_index = Column(Integer, nullable=True)

    exam = relationship("Exam", back_populates="questions")
    exam_answers = relationship("ExamAnswer", back_populates="question", cascade="all, delete-orphan")


class ExamResult(Base):
    __tablename__ = "exam_results"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    exam_id = Column(String, ForeignKey("exams.id", ondelete="CASCADE"), nullable=False)
    user_id = Column(String, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    score = Column(String(50), nullable=True)
    total = Column(String(50), nullable=True)
    percentage = Column(String(50), nullable=True)
    time_taken_seconds = Column(String(50), nullable=True)
    status = Column(String(50), default="in_progress")
    started_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    completed_at = Column(DateTime(timezone=True), nullable=True)

    exam = relationship("Exam", back_populates="results")
    user = relationship("User", back_populates="exam_results")
    answers = relationship("ExamAnswer", back_populates="result", cascade="all, delete-orphan")


class ExamAnswer(Base):
    __tablename__ = "exam_answers"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    result_id = Column(String, ForeignKey("exam_results.id", ondelete="CASCADE"), nullable=False)
    question_id = Column(String, ForeignKey("exam_questions.id", ondelete="CASCADE"), nullable=False)
    selected_answer = Column(String(50), nullable=True)
    is_correct = Column(Boolean, default=False)

    result = relationship("ExamResult", back_populates="answers")
    question = relationship("ExamQuestion", back_populates="exam_answers")



