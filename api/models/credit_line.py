from datetime import datetime
from typing import Optional
from pydantic import BaseModel, Field


class CreditLine(BaseModel):
    amount: float = Field(..., gt=0, description="Credit line amount")
    product_id: str = Field(..., description="ID of the associated financial product")
    user_id: str = Field(..., description="ID of the user requesting the Credit line")
    term_months: int = Field(..., gt=0, description="Credit line term in months")
    created_by: str = None
    created_at: datetime = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    active: Optional[bool] = None
