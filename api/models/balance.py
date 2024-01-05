from dataclasses import Field
from typing import Optional
from datetime import datetime
from pydantic import BaseModel


class Balance(BaseModel):
    payment_id: Optional[str] = None
    amount: Optional[float] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    created_by: Optional[str] = None
    updated_by: Optional[str] = None
