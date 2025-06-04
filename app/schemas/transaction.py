from pydantic import BaseModel
from datetime import datetime
from typing import Optional

class TransactionBase(BaseModel):
    amount: float
    currency: str = "USD"
    description: Optional[str] = None

class TransactionCreate(TransactionBase):
    pass

class TransactionInDB(TransactionBase):
    transaction_id: int
    user_id: int
    status: str
    created_at: datetime
    completed_at: Optional[datetime] = None
    
    class Config:
        orm_mode = True

class TransactionUpdate(BaseModel):
    status: Optional[str] = None
    completed_at: Optional[datetime] = None