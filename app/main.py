from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
import uuid
from contextlib import asynccontextmanager

from app.database import engine, get_db, Base
from app import crud
from app.schemas import UserCreate, UserRead, UserUpdate


# ✅ lifespan (correct way)
@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield


# ✅ SINGLE app instance ONLY
app = FastAPI(
    title="Module10AssignmentKV - Secure User API",
    description="FastAPI + PostgreSQL + SQLAlchemy",
    version="1.0.0",
    lifespan=lifespan
)


@app.get("/")
def root():
    return {"status": "ok"}


@app.get("/health")
def health_check():
    return {"status": "healthy"}


@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered.")
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered.")

    try:
        return crud.create_user(db, user_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User creation failed.")


@app.get("/users/", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_users(db, skip, limit)


@app.get("/users/{user_id}", response_model=UserRead)
def get_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.patch("/users/{user_id}", response_model=UserRead)
def update_user(user_id: uuid.UUID, user_update: UserUpdate, db: Session = Depends(get_db)):
    user = crud.update_user(db, user_id, user_update)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user


@app.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_user(user_id: uuid.UUID, db: Session = Depends(get_db)):
    success = crud.delete_user(db, user_id)
    if not success:
        raise HTTPException(status_code=404, detail="User not found")