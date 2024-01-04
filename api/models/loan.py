from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class Loan(BaseModel):
    amount: float = Field(..., gt=0, description="Loan amount")
    product_id: str = Field(..., description="ID of the associated financial product")
    user_id: str = Field(..., description="ID of the user requesting the loan")
    term_months: int = Field(..., gt=0, description="Loan term in months")
    created_by: str = None
    created_at: datetime = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    active: Optional[bool] = None
