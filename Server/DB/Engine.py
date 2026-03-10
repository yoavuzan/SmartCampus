import os
from sqlmodel import SQLModel
from .database import engine
from .schemas.StudentCourseLink import StudentCourseLink
from .schemas.Student import Student
from .schemas.Lecturer import Lecturer
from .schemas.Classroom import Classroom
from .schemas.Exam import Exam
from .schemas.Course import Course

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    # RUN the seed script to populate the database with initial data
    from .seed import seed_db
    seed_db()
