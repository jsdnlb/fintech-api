from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from datetime import datetime
from api.dependencies import get_loan, get_user
from api.models.payment import Payment
from api.models.user import User
from api.security.authentication import get_user_disabled_current
from api.db.database import database as db


router = APIRouter()
now = datetime.now()
payments = db.payments


@router.post("/payments/", response_model=dict)
def create_payment(
    payment_data: Payment,
    current_user: User = Depends(get_user_disabled_current),
    loan: dict = Depends(get_loan),
    user: dict = Depends(get_user),
):
    payment = payment_data.__dict__
    payment["loan_id"] = str(loan["_id"])
    payment["user_id"] = str(user["_id"])
    payment["created_by"] = current_user.username
    payment["created_at"] = datetime.timestamp(now)

    result = payments.insert_one(payment)
    payment["_id"] = str(payment["_id"])
    if result.inserted_id:
        # TODO Update amount loan
        return {
            "message": "Payment created successfully",
            "loan_id": str(result.inserted_id),
            "payment": payment,
        }

    return payment