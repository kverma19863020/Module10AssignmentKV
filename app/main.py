from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid

from app.database import engine, get_db, Base
from app.models import User
from app.schemas import UserCreate, UserRead, UserUpdate
from app import crud



app = FastAPI(
    title="Module10AssignmentKV - Secure User API",
    description="A FastAPI application with PostgreSQL, SQLAlchemy, Pydantic, and CI/CD via GitHub Actions.",
    version="1.0.0",
)


@app.get("/", tags=["Health"])
def root():
    return {"status": "ok", "message": "Module10AssignmentKV API is running."}


@app.get("/health", tags=["Health"])
def health_check():
    return {"status": "healthy"}


@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED, tags=["Users"])
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered.")
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered.")
    try:
        return crud.create_user(db, user_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User creation failed due to a conflict.")


@app.get("/users/", response_model=list[UserRead], tags=["Users"])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_users(db, skip=skip, limit=limit)


@app.get("/users/{user_id}", response_model=UserRead, tags=["Users"])
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_id(db, user_id)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return db_user


@app.patch("/users/{user_id}", response_model=UserRead, tags=["Users"])
def update_user(user_id: uuid.UUID, user_update: UserUpdate, db: Session = Depends(get_db)):
    db_user = crud.update_user(db, user_id, user_update)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found.")
    return db_user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT, tags=["Users"])
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found.")
