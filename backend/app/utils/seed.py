from sqlalchemy.orm import Session
from app.database.base import SessionLocal, engine, Base
from app.models.subject import Subject
from app.models.lesson import Lesson, Topic
from app.models.quiz import Quiz, Question
from app.models.exam import Exam, ExamQuestion
from app.models.question_pool import QuestionPool
from app.utils.seed_data import SUBJECTS_DATA
from app.utils.exam_standards import JAMB_STANDARDS, WAEC_STANDARDS


def seed_database():
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()

    try:
        existing_count = db.query(Subject).count()
        if existing_count > 0:
            db.close()
            return

        for subj_data in SUBJECTS_DATA:
            lessons_data = subj_data.pop("lessons", [])
            subject = Subject(**subj_data)
            db.add(subject)
            db.flush()

            for lesson_data in lessons_data:
                topics_data = lesson_data.pop("topics", [])
                lesson = Lesson(subject_id=subject.id, **lesson_data)
                db.add(lesson)
                db.flush()

                for topic_data in topics_data:
                    topic = Topic(lesson_id=lesson.id, **topic_data)
                    db.add(topic)

        db.commit()

        for subj_data in SUBJECTS_DATA:
            subject = db.query(Subject).filter(Subject.slug == subj_data["slug"]).first()
            if not subject:
                continue

            jamb_std = JAMB_STANDARDS.get(subject.slug)
            waec_std = WAEC_STANDARDS.get(subject.slug)

            if subject.slug == "mathematics":
                quiz = Quiz(
                    subject_id=subject.id,
                    title="Algebra Basics Quiz",
                    description="Test your understanding of basic algebra concepts",
                    difficulty="easy",
                    time_limit_minutes=15,
                    pass_percentage=50,
                )
                db.add(quiz)
                db.flush()

                questions = [
                    Question(quiz_id=quiz.id, text="What is the value of x in 2x + 5 = 15?", options=["A) 5", "B) 10", "C) 7.5", "D) 20"], correct_answer="A", explanation="2x + 5 = 15, so 2x = 10, therefore x = 5", question_type="multiple_choice", order_index=1),
                    Question(quiz_id=quiz.id, text="Simplify: 3(a + 2b) - 2(a - b)", options=["A) a + 8b", "B) a + 4b", "C) 5a + 4b", "D) a - 4b"], correct_answer="A", explanation="3(a + 2b) - 2(a - b) = 3a + 6b - 2a + 2b = a + 8b", question_type="multiple_choice", order_index=2),
                    Question(quiz_id=quiz.id, text="Which of the following is a variable?", options=["A) 5", "B) x", "C) 10", "D) 100"], correct_answer="B", explanation="A variable is a symbol that represents an unknown value", question_type="multiple_choice", order_index=3),
                    Question(quiz_id=quiz.id, text="Solve: 4x - 7 = 13", options=["A) 5", "B) 1.5", "C) 20", "D) -5"], correct_answer="A", explanation="4x - 7 = 13, 4x = 20, x = 5", question_type="multiple_choice", order_index=4),
                    Question(quiz_id=quiz.id, text="What is the coefficient in 5x²?", options=["A) 2", "B) x", "C) 5", "D) x²"], correct_answer="C", explanation="The coefficient is the numerical factor multiplying the variable", question_type="multiple_choice", order_index=5),
                ]
                for q in questions:
                    db.add(q)

                db.commit()

            quiz = Quiz(
                subject_id=subject.id,
                title=f"{subject.name} Practice Quiz",
                description=f"Test your knowledge of {subject.name}",
                difficulty="medium",
                time_limit_minutes=15,
                pass_percentage=50,
            )
            db.add(quiz)
            db.flush()

            qs = [
                Question(quiz_id=quiz.id, text=f"Sample question about {subject.name}?", options=["A) Option A", "B) Option B", "C) Option C", "D) Option D"], correct_answer="A", explanation=f"Explanation for the {subject.name} question.", question_type="multiple_choice", order_index=1),
                Question(quiz_id=quiz.id, text=f"Second question about {subject.name}?", options=["A) Option A", "B) Option B", "C) Option C", "D) Option D"], correct_answer="B", explanation=f"Explanation for the {subject.name} question.", question_type="multiple_choice", order_index=2),
                Question(quiz_id=quiz.id, text=f"Third question about {subject.name}?", options=["A) Option A", "B) Option B", "C) Option C", "D) Option D"], correct_answer="C", explanation=f"Explanation for the {subject.name} question.", question_type="multiple_choice", order_index=3),
            ]
            for q in qs:
                db.add(q)

            for exam_type, standards in [("JAMB", jamb_std), ("WAEC", waec_std)]:
                if not standards:
                    continue

                q_count = standards["questions"]
                t_minutes = standards["minutes"]

                exam = Exam(
                    subject_id=subject.id,
                    title=f"{subject.name} {exam_type} Mock Exam",
                    description=f"Full {exam_type}-standard mock exam for {subject.name}. {q_count} questions in {t_minutes} minutes covering the complete syllabus.",
                    exam_type=exam_type,
                    year="2025",
                    time_limit_minutes=t_minutes,
                    total_questions=q_count,
                    pass_percentage=40,
                )
                db.add(exam)

            db.commit()

        db.close()
    except Exception:
        db.rollback()
        db.close()
        raise


if __name__ == "__main__":
    seed_database()
