from typing import Optional
from sqlmodel import Field, SQLModel

class Lecturer(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    first_name: str
    last_name: str
    email: str = Field(unique=True, index=True)
    department: str 
    is_active: bool = Field(default=True)
