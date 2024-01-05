from typing import List
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException
from passlib.context import CryptContext
from datetime import datetime
from api.models.balance import Balance
from api.routers.utils.helpers import calculate_loan_installments
from api.routers.utils.exception_handler import exception_handler
from api.models.credit_line import CreditLine
from api.models.user import User
from api.security.authentication import (
    get_user_admin_current,
    get_user_disabled_current,
)
from api.db.database import database as db

router = APIRouter()
balances = db.balances
now = datetime.now()


@router.get("/balances/")
def get_all_balance(user: User = Depends(get_user_disabled_current)):
    all_records = [x for x in balances.find()]
    balance_ids = [str(balance["_id"]) for balance in all_records]

    for item in all_records:
        item["_id"] = str(item["_id"])

    return {
        "message": "List of balances",
        "balance_ids": balance_ids,
        "result": all_records,
    }


@router.delete("/balances/")
def delete_balances(
    user: User = Depends(get_user_disabled_current),
    ids: List[str] = Body(..., required=True),
):
    if not ids:
        raise exception_handler("422_NO_ID")

    object_ids = [ObjectId(id) for id in ids]
    deleted_count = balances.delete_many({"_id": {"$in": object_ids}})

    if deleted_count.deleted_count == 0:
        raise exception_handler("404_NOT_FOUND")

    return {
        "message": "Balance deleted",
        "deleted_count": deleted_count.deleted_count,
    }
