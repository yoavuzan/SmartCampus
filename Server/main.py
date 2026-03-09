from typing import Annotated
from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from sqlmodel import Session, select
from DB.Engine import create_db_and_tables, engine
from DB.schemas.Student import Student
from config import settings
from utils.security import verify_password, create_access_token

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Run when the server starts
    create_db_and_tables()
    yield
    # Run when the server shuts down
    pass

app = FastAPI(lifespan=lifespan)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get a DB session
def get_session():
    with Session(engine) as session:
        yield session

@app.post("/token")
async def login(
    form_data: Annotated[OAuth2PasswordRequestForm, Depends()],
    session: Session = Depends(get_session)
):
    # Find student by email (using username field from form)
    statement = select(Student).where(Student.email == form_data.username)
    student = session.exec(statement).first()

    if not student:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Verify password using the security utility
    if not verify_password(form_data.password, student.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create a real JWT access token
    access_token = create_access_token(data={"sub": student.email})
    return {
        "access_token": access_token,
        "token_type": "bearer"
    }

@app.get("/")
def root():
    return {"message": "SmartCampus API is Running!"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

