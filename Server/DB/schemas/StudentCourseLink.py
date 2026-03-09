from typing import Optional
from sqlmodel import Field, SQLModel

class StudentCourseLink(SQLModel, table=True):
    student_id: Optional[int] = Field(
        default=None, foreign_key="student.id", primary_key=True
    )
    course_id: Optional[int] = Field(
        default=None, foreign_key="course.id", primary_key=True
    )
