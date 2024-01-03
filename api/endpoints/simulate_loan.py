from typing import List
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException
from passlib.context import CryptContext
from datetime import datetime
from api.endpoints.exception_handler import exception_handler
from api.endpoints.utils.helpers import calculate_loan_installments
from api.models.loans import Loan
from api.models.user import User
from api.security.authentication import (
    get_user_admin_current,
)
from api.db.database import database as db


router = APIRouter()
users = db.users
products = db.products
loans = db.loans
now = datetime.now()


@router.post("/simulate_loan/")
def create_loan(loan_data: Loan, current_user: User = Depends(get_user_admin_current)):
    loan = loan_data.__dict__
    product = products.find_one({"_id": ObjectId(loan["product_id"])})
    if product:
        if (
            loan["amount"] > product["max_amount"]
            or loan["amount"] < product["min_amount"]
        ):
            return (
                HTTPException(
                    status_code=500,
                    detail="Amount is higher or lower than expected",
                ),
            )
        amount_interes = (product["interest_rate"] * 100) / 360 * loan["amount"]
        if product["discount"] > 0:
            amount_interes = amount_interes - amount_interes * product["discount"]
        total_payable = loan["amount"] + amount_interes
        quotas = calculate_loan_installments(
            float(total_payable),
            int(loan["term_months"]),
        )
        loan["financial_product"] = product
        loan["financial_product"]["_id"] = str(loan["financial_product"]["_id"])
        loan["created_by"] = current_user.username
        loan["created_at"] = datetime.timestamp(now)
        loan["amount_interes"] = amount_interes
        loan["total_payable"] = total_payable
        loan["quotas"] = quotas

        return loan
    else:
        raise exception_handler("404_NOT_FOUND")
