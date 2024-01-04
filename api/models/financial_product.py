from typing import Optional
from pydantic import BaseModel
from datetime import datetime


class FinancialProduct(BaseModel):
    name: Optional[str] = None
    product_type: Optional[str] = None
    interest_rate: Optional[float] = None
    min_amount: Optional[float] = None
    max_amount: Optional[float] = None
    discount: Optional[float] = None
    created_by: str = None
    created_at: datetime = None
    updated_by: Optional[str] = None
    updated_at: Optional[datetime] = None
    active: Optional[bool] = None
