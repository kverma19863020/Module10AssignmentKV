from fastapi import FastAPI, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from contextlib import asynccontextmanager
import uuid

from app.database import engine, get_db, Base
from app import crud
from app.schemas import UserCreate, UserRead, UserUpdate


# ✅ Lifespan (correct FastAPI modern way)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # create tables on startup (works in CI + Docker)
    Base.metadata.create_all(bind=engine)
    yield
    # optional cleanup after shutdown


# ✅ SINGLE FastAPI APP (DO NOT CREATE ANOTHER ONE)
app = FastAPI(
    title="Module10AssignmentKV - Secure User API",
    description="FastAPI + PostgreSQL + SQLAlchemy + CI/CD",
    version="1.0.0",
    lifespan=lifespan
)


# -------------------------
# HEALTH ROUTES
# -------------------------
@app.get("/")
def root():
    return {"status": "ok", "message": "API is running"}


@app.get("/health")
def health():
    return {"status": "healthy"}


# -------------------------
# USER ROUTES
# -------------------------
@app.post("/users/", response_model=UserRead, status_code=status.HTTP_201_CREATED)
def create_user(user_in: UserCreate, db: Session = Depends(get_db)):
    # duplicate checks
    if crud.get_user_by_username(db, user_in.username):
        raise HTTPException(status_code=400, detail="Username already registered")
    if crud.get_user_by_email(db, user_in.email):
        raise HTTPException(status_code=400, detail="Email already registered")

    try:
        return crud.create_user(db, user_in)
    except IntegrityError:
        db.rollback()
        raise HTTPException(status_code=400, detail="User creation failed")


@app.get("/users/", response_model=list[UserRead])
def list_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    return crud.get_all_users(db, skip=skip, limit=limit)


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