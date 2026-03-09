from typing import Optional, List
from sqlmodel import Field, SQLModel, Relationship
from .StudentCourseLink import StudentCourseLink

class Course(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str
    code: str = Field(unique=True, index=True)
    description: Optional[str] = None
    credits: int = 3

    lecturer_id: Optional[int] = Field(default=None, foreign_key="lecturer.id")

    # Many-to-many relationship
    students: List["Student"] = Relationship(back_populates="courses", link_model=StudentCourseLink)

    classroom_id: Optional[int] = Field(default=None, foreign_key="classroom.id")
