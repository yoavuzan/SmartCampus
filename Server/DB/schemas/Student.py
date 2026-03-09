from typing import Optional, List
from enum import Enum
from sqlmodel import Field, SQLModel, Relationship
from .StudentCourseLink import StudentCourseLink

class UserRole(str, Enum):
    STUDENT = "student"
    ADMIN = "admin"

class Student(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str

    email: str = Field(unique=True, index=True)

    hashed_password: str

    role: UserRole = Field(default=UserRole.STUDENT)

    age: Optional[int] = None
    major: Optional[str] = "Computer Science"
    is_active: bool = Field(default=True)

    # Many-to-many relationship
    courses: List["Course"] = Relationship(back_populates="students", link_model=StudentCourseLink)
