from sqlalchemy.orm import Session
from app.database.base import SessionLocal, engine, Base
from app.models.subject import Subject
from app.models.lesson import Lesson, Topic
from app.models.quiz import Quiz, Question
from app.models.exam import Exam, ExamQuestion
from app.utils.seed_data import SUBJECTS_DATA


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

        math = db.query(Subject).filter(Subject.slug == "mathematics").first()
        if math:
            quiz = Quiz(
                subject_id=math.id,
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

        for subj_data in SUBJECTS_DATA:
            subject = db.query(Subject).filter(Subject.slug == subj_data["slug"]).first()
            if subject and subj_data["slug"] not in ["mathematics"]:
                quiz = Quiz(
                    subject_id=subject.id,
                    title=f"{subj_data['name']} Basics Quiz",
                    description=f"Test your knowledge of {subj_data['name']}",
                    difficulty="medium",
                    time_limit_minutes=15,
                    pass_percentage=50,
                )
                db.add(quiz)
                db.flush()

                qs = [
                    Question(quiz_id=quiz.id, text=f"Sample question about {subj_data['name']}?", options=["A) Option A", "B) Option B", "C) Option C", "D) Option D"], correct_answer="A", explanation=f"Explanation for the {subj_data['name']} question.", question_type="multiple_choice", order_index=1),
                    Question(quiz_id=quiz.id, text=f"Second question about {subj_data['name']}?", options=["A) Option A", "B) Option B", "C) Option C", "D) Option D"], correct_answer="B", explanation=f"Explanation for the {subj_data['name']} question.", question_type="multiple_choice", order_index=2),
                    Question(quiz_id=quiz.id, text=f"Third question about {subj_data['name']}?", options=["A) Option A", "B) Option B", "C) Option C", "D) Option D"], correct_answer="C", explanation=f"Explanation for the {subj_data['name']} question.", question_type="multiple_choice", order_index=3),
                ]
                for q in qs:
                    db.add(q)

                exam = Exam(
                    subject_id=subject.id,
                    title=f"{subj_data['name']} Mock Exam",
                    description=f"Practice {subj_data['name']} with exam-style questions",
                    exam_type="WAEC",
                    year="2024",
                    time_limit_minutes=60,
                    total_questions=50,
                    pass_percentage=40,
                )
                db.add(exam)
                db.flush()

                for i in range(5):
                    eq = ExamQuestion(
                        exam_id=exam.id,
                        text=f"Exam question {i+1} about {subj_data['name']}?",
                        options=["A) Option A", "B) Option B", "C) Option C", "D) Option D"],
                        correct_answer=["A", "B", "C", "D"][i % 4],
                        explanation=f"Explanation for exam question {i+1}.",
                        order_index=i + 1,
                    )
                    db.add(eq)

                db.commit()

        db.close()
    except Exception:
        db.rollback()
        db.close()
        raise


if __name__ == "__main__":
    seed_database()
