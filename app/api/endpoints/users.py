from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas.user import UserCreate, UserInDB, UserUpdate
from app.crud import crud_user

router = APIRouter()

@router.post("/", response_model=UserInDB)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    db_user = crud_user.get_user_by_username(db, username=user.username)
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud_user.create_user(db=db, user=user)

@router.get("/me", response_model=UserInDB)
def read_user_me(
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = crud_user.get_user_by_username(db, username=current_user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user

@router.put("/me", response_model=UserInDB)
def update_user_me(
    user_update: UserUpdate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = crud_user.get_user_by_username(db, username=current_user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    return crud_user.update_user(db=db, user_id=db_user.user_id, user_update=user_update)