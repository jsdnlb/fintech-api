from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException, Body
from typing import List
from datetime import datetime
from api.dependencies import get_credit_line, get_user
from api.models.payment import Payment
from api.models.user import User
from api.routers.utils.exception_handler import exception_handler
from api.security.authentication import get_user_disabled_current
from api.db.database import database as db


router = APIRouter()
now = datetime.now()
payments = db.payments


@router.get("/payments/")
def get_all_payments(user: User = Depends(get_user_disabled_current)):
    all_records = [x for x in payments.find()]
    payment_ids = [str(payment["_id"]) for payment in all_records]

    for item in all_records:
        item["_id"] = str(item["_id"])

    return {
        "message": "List of payments",
        "payment_ids": payment_ids,
        "result": all_records,
    }


@router.post("/payments/", response_model=dict)
def create_payment(
    payment_data: Payment,
    current_user: User = Depends(get_user_disabled_current),
    credit_line: dict = Depends(get_credit_line),
    user: dict = Depends(get_user),
):
    payment = payment_data.__dict__
    payment["credit_line_id"] = str(credit_line["_id"])
    payment["user_id"] = str(user["_id"])
    payment["created_by"] = current_user.id
    payment["created_at"] = datetime.timestamp(now)

    result = payments.insert_one(payment)
    payment["_id"] = str(payment["_id"])
    if result.inserted_id:
        # TODO Update amount credit line
        return {
            "message": "Payment created successfully",
            "credit_line_id": str(result.inserted_id),
            "payment": payment,
        }

    return payment


@router.delete("/payments/")
def delete_payments(
    user: User = Depends(get_user_disabled_current),
    ids: List[str] = Body(..., required=True),
):
    if not ids:
        raise exception_handler("422_NO_ID")

    object_ids = [ObjectId(id) for id in ids]
    deleted_count = payments.delete_many({"_id": {"$in": object_ids}})

    if deleted_count.deleted_count == 0:
        raise exception_handler("404_NOT_FOUND")

    return {
        "message": "Payments deleted",
        "deleted_count": deleted_count.deleted_count,
    }
