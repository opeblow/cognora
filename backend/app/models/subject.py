import uuid
from sqlalchemy import Column, String, Integer, Text
from sqlalchemy.orm import relationship
from app.database.base import Base


class Subject(Base):
    __tablename__ = "subjects"

    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String(255), nullable=False, unique=True)
    slug = Column(String(255), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    category = Column(String(50), nullable=False)
    icon = Column(String(50), nullable=True)
    color = Column(String(7), nullable=True)
    order_index = Column(Integer, nullable=True)

    chapters = relationship("Chapter", back_populates="subject", cascade="all, delete-orphan")
    lessons = relationship("Lesson", back_populates="subject", cascade="all, delete-orphan")
    quizzes = relationship("Quiz", back_populates="subject", cascade="all, delete-orphan")
    exams = relationship("Exam", back_populates="subject", cascade="all, delete-orphan")



