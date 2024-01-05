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
users = db.users
products = db.products
balances = db.balances
credit_line_db = db.credit_line
now = datetime.now()


@router.get("/credit_line/")
def get_all_credit_line(user: User = Depends(get_user_disabled_current)):
    all_records = [x for x in credit_line_db.find()]
    credit_line_ids = [str(credit_line["_id"]) for credit_line in all_records]

    for item in all_records:
        item["_id"] = str(item["_id"])

        if "financial_product" in item:
            item["financial_product"]["_id"] = str(item["financial_product"]["_id"])

    return {
        "message": "List of credit line",
        "credit_line_ids": credit_line_ids,
        "result": all_records,
    }


@router.get("/credit_line/{credit_line}")
def get_credit_line_by_id(
    credit_line: str, current_user: User = Depends(get_user_disabled_current)
):
    credit_line = credit_line_db.find_one({"_id": ObjectId(credit_line)})

    if credit_line:
        if "financial_product" in credit_line:
            credit_line["financial_product"]["_id"] = str(
                credit_line["financial_product"]["_id"]
            )
        credit_line["_id"] = str(credit_line["_id"])
        return credit_line
    else:
        raise exception_handler("404_NOT_FOUND")


@router.post("/credit_line/")
def create_credit_line(
    credit_line_data: CreditLine, current_user: User = Depends(get_user_admin_current)
):
    balance = {}
    credit_line = credit_line_data.__dict__
    user = users.find_one({"_id": ObjectId(credit_line["user_id"])})
    financial_product = products.find_one({"_id": ObjectId(credit_line["product_id"])})
    if user and financial_product:
        if (
            credit_line["amount"] > financial_product["max_amount"]
            or credit_line["amount"] < financial_product["min_amount"]
        ):
            return (
                HTTPException(
                    status_code=500,
                    detail="Amount is higher or lower than expected",
                ),
            )
        amount_interes = (
            financial_product["interest_rate"] / 360 * credit_line["amount"]
        )
        total_payable = credit_line["amount"] + amount_interes
        quota = calculate_loan_installments(
            float(total_payable),
            int(credit_line["term_months"]),
        )
        credit_line["financial_product"] = financial_product
        credit_line["created_by"] = current_user.username
        credit_line["created_at"] = datetime.timestamp(now)
        credit_line["amount_interes"] = amount_interes
        credit_line["total_payable"] = total_payable
        credit_line["quota"] = quota
        res_credit_line = credit_line_db.insert_one(credit_line)

        balance["balance"] = -total_payable
        balance["credit_line_id"] = str(res_credit_line.inserted_id)
        balance["created_by"] = current_user.username
        balance["created_at"] = datetime.timestamp(now)
        res_balance = balances.insert_one(balance)
        if res_credit_line.inserted_id and res_balance:
            return {
                "message": "Credit line created successfully",
                "credit_line_id": str(res_credit_line.inserted_id),
                "balance_id": str(res_balance.inserted_id),
            }
        else:
            raise exception_handler("500_CREATE")
    else:
        raise exception_handler("404_NOT_FOUND")


@router.delete("/credit_line/")
def delete_credit_lines(
    user: User = Depends(get_user_disabled_current),
    ids: List[str] = Body(..., required=True),
):
    if not ids:
        raise exception_handler("422_NO_ID")

    object_ids = [ObjectId(id) for id in ids]
    deleted_count = credit_line_db.delete_many({"_id": {"$in": object_ids}})

    if deleted_count.deleted_count == 0:
        raise exception_handler("404_NOT_FOUND")

    return {
        "message": "Credit line deleted",
        "deleted_count": deleted_count.deleted_count,
    }
