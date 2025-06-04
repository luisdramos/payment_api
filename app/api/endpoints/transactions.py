from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List
from app.core.security import get_current_user
from app.db.session import get_db
from app.schemas import transaction
from app.crud import crud_transaction, crud_user

router = APIRouter()

@router.post("/", response_model=transaction.TransactionInDB)
def create_transaction(
    transaction_data: transaction.TransactionCreate,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = crud_user.get_user_by_username(db, username=current_user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    try:
        return crud_transaction.create_transaction(
            db=db,
            transaction=transaction_data,
            user_id=db_user.user_id
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/", response_model=List[transaction.TransactionInDB])
def read_user_transactions(
    skip: int = 0,
    limit: int = 10,
    current_user: str = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    db_user = crud_user.get_user_by_username(db, username=current_user)
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    
    transactions = crud_transaction.get_user_transactions(
        db=db,
        user_id=db_user.user_id,
        skip=skip,
        limit=limit
    )
    return transactions