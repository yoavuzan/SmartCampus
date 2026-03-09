from sqlmodel import Session, select
import sys
import os

# This file is designed to be imported from Engine.py OR run directly
try:
    # If imported as part of the package (e.g., from Engine.py)
    from .Engine import engine
    from .schemas.Student import Student, UserRole
except (ImportError, ValueError):
    # If run directly as a script
    from Engine import engine
    from schemas.Student import Student, UserRole

# Add the Server directory to sys.path to import from utils if run directly
if __name__ == "__main__":
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.security import get_password_hash

def seed_db():
    # Tables are already created by the time this is called from Engine.py
    
    with Session(engine) as session:
        # Check if the student already exists
        statement = select(Student).where(Student.email == "test@student.com")
        existing_student = session.exec(statement).first()
        
        if existing_student:
            print(f"Student {existing_student.email} already exists.")
            return

        print("Seeding database...")
        # Create a test student
        test_student = Student(
            first_name="Test",
            last_name="Student",
            email="test@student.com",
            hashed_password=get_password_hash("password123"),
            role=UserRole.STUDENT,
            age=20,
            major="Software Engineering"
        )
        
        session.add(test_student)
        session.commit()
        print(f"Added student: {test_student.email}")

if __name__ == "__main__":
    seed_db()
