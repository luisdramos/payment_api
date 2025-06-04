from sqlalchemy.orm import Session
from sqlalchemy import text
from app.db import models
from app.schemas import transaction
from typing import List

def get_transaction(db: Session, transaction_id: int):
    return db.query(models.Transaction).filter(models.Transaction.transaction_id == transaction_id).first()

def get_user_transactions(db: Session, user_id: int, skip: int = 0, limit: int = 10) -> List[models.Transaction]:
    # Using the stored procedure we created
    result = db.execute(
        text("SELECT * FROM get_user_transactions(:user_id, :limit, :offset)"),
        {"user_id": user_id, "limit": limit, "offset": skip}
    )
    return result.fetchall()

def create_transaction(db: Session, transaction: transaction.TransactionCreate, user_id: int):
    # Using the stored procedure we created
    result = db.execute(
        text("CALL start_transaction(:user_id, :amount, :currency, :description, NULL, NULL)"),
        {
            "user_id": user_id,
            "amount": transaction.amount,
            "currency": transaction.currency,
            "description": transaction.description
        }
    )
    db.commit()
    
    # Get the last inserted transaction for this user
    last_transaction = db.query(models.Transaction)\
        .filter(models.Transaction.user_id == user_id)\
        .order_by(models.Transaction.transaction_id.desc())\
        .first()
    
    return last_transaction

def update_transaction_status(db: Session, transaction_id: int, status: str):
    db_transaction = get_transaction(db, transaction_id)
    if not db_transaction:
        return None
    
    db_transaction.status = status
    if status == "completed":
        db_transaction.completed_at = func.now()
    
    db.add(db_transaction)
    db.commit()
    db.refresh(db_transaction)
    return db_transaction