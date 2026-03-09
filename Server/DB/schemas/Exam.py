from typing import Optional, Annotated
from datetime import datetime
from sqlmodel import Field, SQLModel

class Exam(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    date: datetime
    
    
    classroom_id: Optional[int] = Field(default=None, foreign_key="classroom.id")
    lecturer_id: Optional[int] = Field(default=None, foreign_key="lecturer.id")
    course_id: Optional[int] = Field(default=None, foreign_key="course.id")
