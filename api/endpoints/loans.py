from typing import List
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException
from passlib.context import CryptContext
from datetime import datetime
from api.endpoints.exception_handler import exception_handler
from api.models.loans import Loan
from api.models.user import User
from api.security.authentication import (
    get_user_admin_current,
    get_user_disabled_current,
)
from api.db.database import database as db


router = APIRouter()
users = db.users
products = db.products
loans = db.loans
now = datetime.now()


@router.get("/loans/")
def get_all_loans(user: User = Depends(get_user_disabled_current)):
    all_records = [x for x in loans.find()]
    loan_ids = [str(loan["_id"]) for loan in all_records]

    for item in all_records:
        item["_id"] = str(item["_id"])

        if "financial_product" in item:
            item["financial_product"]["_id"] = str(item["financial_product"]["_id"])

    return {
        "message": "List of loans",
        "loans_ids": loan_ids,
        "result": all_records,
    }


@router.get("/loans/{loan_id}")
def get_loans_by_id(
    loan_id: str, current_user: User = Depends(get_user_disabled_current)
):
    loan = loans.find_one({"_id": ObjectId(loan_id)})

    if loan:
        if "financial_product" in loan:
            loan["financial_product"]["_id"] = str(loan["financial_product"]["_id"])
        loan["_id"] = str(loan["_id"])
        return loan
    else:
        raise exception_handler("404_NOT_FOUND")


@router.post("/loans/")
def create_loan(loan: Loan, current_user: User = Depends(get_user_admin_current)):
    loan_data = loan.__dict__
    user = users.find_one({"_id": ObjectId(loan_data["user_id"])})
    financial_product = products.find_one({"_id": ObjectId(loan_data["product_id"])})
    if user and financial_product:
        if (
            loan_data["amount"] > financial_product["max_amount"]
            or loan_data["amount"] < financial_product["min_amount"]
        ):
            return (
                HTTPException(
                    status_code=500,
                    detail="Amount is higher or lower than expected",
                ),
            )
        amount_interes = financial_product["interest_rate"] / 360 * loan_data["amount"]
        total_payable = loan_data["amount"] + amount_interes
        quota = calculate_loan_installments(
            float(total_payable),
            int(loan_data["term_months"]),
        )
        loan_data["financial_product"] = financial_product
        loan_data["created_by"] = current_user.username
        loan_data["created_at"] = datetime.timestamp(now)
        loan_data["amount_interes"] = amount_interes
        loan_data["total_payable"] = total_payable
        loan_data["quota"] = quota
        result = loans.insert_one(loan_data)
        if result.inserted_id:
            return {
                "message": "Loan created successfully",
                "loan_id": str(result.inserted_id),
            }
        else:
            raise exception_handler("500_CREATE")
    else:
        raise exception_handler("404_NOT_FOUND")


def calculate_loan_installments(total_amount, term_months):
    amount_quota = total_amount / term_months
    amount = 0
    installments = {}

    for month in range(1, term_months + 1):
        amount = amount + amount_quota
        installments[str(month)] = round(amount, 2)
    return installments


@router.delete("/loans/")
def delete_loans(
    user: User = Depends(get_user_disabled_current),
    ids: List[str] = Body(..., required=True),
):
    if not ids:
        raise exception_handler("422_NO_ID")

    object_ids = [ObjectId(id) for id in ids]
    deleted_count = loans.delete_many({"_id": {"$in": object_ids}})

    if deleted_count.deleted_count == 0:
        raise exception_handler("404_NOT_FOUND")

    return {
        "message": "Loans deleted",
        "deleted_count": deleted_count.deleted_count,
    }
