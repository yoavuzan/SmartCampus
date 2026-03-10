from sqlmodel import select
import sys
import os
from datetime import datetime, timedelta

# This file is designed to be imported from Engine.py OR run directly
try:
    # If imported as part of the package (e.g., from Engine.py)
    from .database import engine
    from .schemas.Student import Student, UserRole
    from .schemas.Lecturer import Lecturer
    from .schemas.Classroom import Classroom
    from .schemas.Exam import Exam
    from .schemas.Course import Course
    from .schemas.StudentCourseLink import StudentCourseLink
    from .schemas import get_db_context
except (ImportError, ValueError):
    # If run directly as a script
    from database import engine
    from schemas.Student import Student, UserRole
    from schemas.Lecturer import Lecturer
    from schemas.Classroom import Classroom
    from schemas.Exam import Exam
    from schemas.Course import Course
    from schemas.StudentCourseLink import StudentCourseLink
    from schemas import get_db_context

# Add the Server directory to sys.path to import from utils if run directly
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.security import get_password_hash

def seed_db():    
    with get_db_context() as session:
        # 1. Seed Student (if not exists)
        if not session.exec(select(Student).where(Student.email == "test@student.com")).first():
            print("מוסיף סטודנט לדוגמה...")
            test_student = Student(
                first_name="ישראל",
                last_name="ישראלי",
                email="test@student.com",
                hashed_password=get_password_hash("password123"),
                role=UserRole.STUDENT,
                age=22,
                major="מדעי המחשב"
            )
            session.add(test_student)
            session.flush() # flush so we get the ID but session remains active
        else:
            test_student = session.exec(select(Student).where(Student.email == "test@student.com")).first()

        # 2. Seed Classrooms
        if not session.exec(select(Classroom)).first():
            c1 = Classroom(building="בניין אקדמי א'", room_number="101", capacity=40, has_projector=True)
            c2 = Classroom(building="בניין מדעים", room_number="202", capacity=60, has_projector=True)
            session.add(c1)
            session.add(c2)
            session.flush()
        else:
            c1 = session.exec(select(Classroom)).first()

        # 3. Seed Lecturers
        if not session.exec(select(Lecturer)).first():
            l1 = Lecturer(first_name="יוסי", last_name="כהן", email="yossi@campus.ac.il", department="מדעי המחשב")
            l2 = Lecturer(first_name="שרה", last_name="לוי", email="sara@campus.ac.il", department="מערכות מידע")
            session.add(l1)
            session.add(l2)
            session.flush()
        else:
            l1 = session.exec(select(Lecturer)).first()

        # 4. Seed Courses
        if not session.exec(select(Course)).first():
            course1 = Course(
                name="מבוא לתכנות", 
                code="CS101", 
                description="קורס יסוד בתכנות פייתון", 
                credits=4,
                lecturer_id=l1.id,
                classroom_id=c1.id
            )
            course2 = Course(
                name="מבני נתונים", 
                code="CS201", 
                description="לימוד מבני נתונים מתקדמים", 
                credits=5,
                lecturer_id=l1.id,
                classroom_id=c1.id
            )
            session.add(course1)
            session.add(course2)
            session.flush()
            
            # Link student to courses
            link1 = StudentCourseLink(student_id=test_student.id, course_id=course1.id)
            link2 = StudentCourseLink(student_id=test_student.id, course_id=course2.id)
            session.add(link1)
            session.add(link2)
        else:
            course1 = session.exec(select(Course)).first()

        # 5. Seed Exams
        if not session.exec(select(Exam)).first():
            print("מוסיף מבחנים...")
            exam1 = Exam(
                subject="מבוא לתכנות - מועד א'",
                date=datetime.now() + timedelta(days=30),
                classroom_id=c1.id,
                lecturer_id=l1.id
            )
            session.add(exam1)

        print("Database seeding completed successfully!")
        # Session commits automatically when exiting with get_db() block if no error

if __name__ == "__main__":
    seed_db()
