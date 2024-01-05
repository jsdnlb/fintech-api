from typing import List
from bson import ObjectId
from fastapi import APIRouter, Body, Depends, HTTPException
from passlib.context import CryptContext
from datetime import datetime
from api.routers.utils.exception_handler import exception_handler
from api.routers.utils.helpers import calculate_loan_installments
from api.models.credit_line import CreditLine
from api.models.user import User
from api.security.authentication import (
    get_user_admin_current,
)
from api.db.database import database as db


router = APIRouter()
users = db.users
products = db.products
now = datetime.now()


@router.post("/simulate_credit_line/")
def simulate_credit_line(
    credit_line_data: CreditLine, current_user: User = Depends(get_user_admin_current)
):
    credit_line = credit_line_data.__dict__
    product = products.find_one({"_id": ObjectId(credit_line["product_id"])})
    if product:
        if (
            credit_line["amount"] > product["max_amount"]
            or credit_line["amount"] < product["min_amount"]
        ):
            return (
                HTTPException(
                    status_code=500,
                    detail="Amount is higher or lower than expected",
                ),
            )
        amount_interes = (product["interest_rate"] * 100) / 360 * credit_line["amount"]
        if product["discount"] > 0:
            amount_interes = amount_interes - amount_interes * product["discount"]
        total_payable = credit_line["amount"] + amount_interes
        quotas = calculate_loan_installments(
            float(total_payable),
            int(credit_line["term_months"]),
        )
        credit_line["financial_product"] = product
        credit_line["financial_product"]["_id"] = str(
            credit_line["financial_product"]["_id"]
        )
        credit_line["created_by"] = current_user.id
        credit_line["created_at"] = datetime.timestamp(now)
        credit_line["amount_interes"] = amount_interes
        credit_line["total_payable"] = total_payable
        credit_line["quotas"] = quotas

        return credit_line
    else:
        raise exception_handler("404_NOT_FOUND")
