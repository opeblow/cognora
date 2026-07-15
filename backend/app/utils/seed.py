from app.database.base import SessionLocal, engine, Base
from app.models.subject import Subject
from app.models.lesson import Lesson, Topic
from app.models.quiz import Quiz
from app.models.exam import Exam
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

            quiz = Quiz(
                subject_id=subject.id,
                title=f"{subject.name} Practice Quiz",
                description=f"Test your knowledge of {subject.name} with 60 AI-generated WAEC/JAMB-standard questions",
                difficulty="medium",
                time_limit_minutes=6,
                pass_percentage=50,
            )
            db.add(quiz)

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
