from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Payment(BaseModel):
    amount: float
    user_id: Optional[str] = None
    loan_id: Optional[str] = None
    payment_date: Optional[datetime] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
