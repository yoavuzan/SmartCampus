from sqlmodel import select, Session
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
        # 1. Seed Students (3 Students)
        students_data = [
            {
                "first_name": "ישראל",
                "last_name": "ישראלי",
                "email": "test@student.com",
                "hashed_password": get_password_hash("password123"),
                "role": UserRole.STUDENT,
                "age": 22,
                "major": "מדעי המחשב"
            },
            {
                "first_name": "נועה",
                "last_name": "לוי",
                "email": "noa@student.com",
                "hashed_password": get_password_hash("password123"),
                "role": UserRole.STUDENT,
                "age": 21,
                "major": "מערכות מידע"
            },
            {
                "first_name": "איתי",
                "last_name": "כהן",
                "email": "itay@student.com",
                "hashed_password": get_password_hash("password123"),
                "role": UserRole.STUDENT,
                "age": 23,
                "major": "הנדסת תוכנה"
            }
        ]
        
        students = []
        for s_data in students_data:
            student = session.exec(select(Student).where(Student.email == s_data["email"])).first()
            if not student:
                student = Student(**s_data)
                session.add(student)
                session.flush()
            students.append(student)

        # 2. Seed Lecturers (3 Lecturers)
        lecturers_data = [
            {"first_name": "יוסי", "last_name": "כהן", "email": "yossi@campus.ac.il", "department": "מדעי המחשב"},
            {"first_name": "שרה", "last_name": "לוי", "email": "sara@campus.ac.il", "department": "מערכות מידע"},
            {"first_name": "אמיר", "last_name": "מזרחי", "email": "amir@campus.ac.il", "department": "הנדסה"}
        ]
        
        lecturers = []
        for l_data in lecturers_data:
            lecturer = session.exec(select(Lecturer).where(Lecturer.email == l_data["email"])).first()
            if not lecturer:
                lecturer = Lecturer(**l_data)
                session.add(lecturer)
                session.flush()
            lecturers.append(lecturer)

        # 3. Seed Classrooms (5 Classrooms)
        classrooms_data = [
            {"building": "בניין אקדמי א'", "room_number": "101", "capacity": 40, "has_projector": True},
            {"building": "בניין מדעים", "room_number": "202", "capacity": 60, "has_projector": True},
            {"building": "בניין הנדסה", "room_number": "303", "capacity": 30, "has_projector": False},
            {"building": "ספרייה מרכזית", "room_number": "אולם 1", "capacity": 100, "has_projector": True},
            {"building": "בניין ניהול", "room_number": "404", "capacity": 25, "has_projector": True}
        ]
        
        classrooms = []
        for c_data in classrooms_data:
            classroom = session.exec(select(Classroom).where(
                Classroom.building == c_data["building"], 
                Classroom.room_number == c_data["room_number"]
            )).first()
            if not classroom:
                classroom = Classroom(**c_data)
                session.add(classroom)
                session.flush()
            classrooms.append(classroom)

        # 4. Seed Courses (5 Courses)
        courses_data = [
            {
                "name": "מבוא לתכנות", 
                "code": "CS101", 
                "description": "קורס יסוד בתכנות פייתון", 
                "credits": 4,
                "lecturer_id": lecturers[0].id,
                "classroom_id": classrooms[0].id
            },
            {
                "name": "מבני נתונים", 
                "code": "CS201", 
                "description": "לימוד מבני נתונים מתקדמים", 
                "credits": 5,
                "lecturer_id": lecturers[0].id,
                "classroom_id": classrooms[1].id
            },
            {
                "name": "אלגוריתמים", 
                "code": "CS301", 
                "description": "תכנון וניתוח אלגוריתמים", 
                "credits": 4,
                "lecturer_id": lecturers[0].id,
                "classroom_id": classrooms[2].id
            },
            {
                "name": "בסיסי נתונים", 
                "code": "IS102", 
                "description": "עקרונות SQL ומסדי נתונים", 
                "credits": 3,
                "lecturer_id": lecturers[1].id,
                "classroom_id": classrooms[3].id
            },
            {
                "name": "רשתות תקשורת", 
                "code": "CS401", 
                "description": "פרוטוקולי תקשורת ואינטרנט", 
                "credits": 4,
                "lecturer_id": lecturers[2].id,
                "classroom_id": classrooms[4].id
            }
        ]
        
        courses = []
        for crs_data in courses_data:
            course = session.exec(select(Course).where(Course.code == crs_data["code"])).first()
            if not course:
                course = Course(**crs_data)
                session.add(course)
                session.flush()
            courses.append(course)

        # Link Students to some courses
        for student in students:
            for course in courses[:3]: # Link to first 3 courses
                link = session.exec(select(StudentCourseLink).where(
                    StudentCourseLink.student_id == student.id,
                    StudentCourseLink.course_id == course.id
                )).first()
                if not link:
                    session.add(StudentCourseLink(student_id=student.id, course_id=course.id))

        # 5. Seed Exams (10 Exams)
        exams_data = [
            {"subject": "מבוא לתכנות - מועד א'", "days": 30, "room": classrooms[0], "lec": lecturers[0]},
            {"subject": "מבוא לתכנות - מועד ב'", "days": 60, "room": classrooms[0], "lec": lecturers[0]},
            {"subject": "מבני נתונים - מועד א'", "days": 35, "room": classrooms[1], "lec": lecturers[0]},
            {"subject": "מבני נתונים - מועד ב'", "days": 65, "room": classrooms[1], "lec": lecturers[0]},
            {"subject": "אלגוריתמים - מועד א'", "days": 40, "room": classrooms[2], "lec": lecturers[0]},
            {"subject": "בסיסי נתונים - מועד א'", "days": 45, "room": classrooms[3], "lec": lecturers[1]},
            {"subject": "רשתות תקשורת - מועד א'", "days": 50, "room": classrooms[4], "lec": lecturers[2]},
            {"subject": "מתמטיקה בדידה - מועד א'", "days": 20, "room": classrooms[1], "lec": lecturers[1]},
            {"subject": "מערכות הפעלה - מועד א'", "days": 55, "room": classrooms[2], "lec": lecturers[2]},
            {"subject": "אנגלית אקדמית - מועד א'", "days": 15, "room": classrooms[3], "lec": lecturers[1]}
        ]
        
        for e_data in exams_data:
            exam = session.exec(select(Exam).where(Exam.subject == e_data["subject"])).first()
            if not exam:
                new_exam = Exam(
                    subject=e_data["subject"],
                    date=datetime.now() + timedelta(days=e_data["days"]),
                    classroom_id=e_data["room"].id,
                    lecturer_id=e_data["lec"].id
                )
                session.add(new_exam)

        print("Database seeding completed successfully!")

if __name__ == "__main__":
    seed_db()
