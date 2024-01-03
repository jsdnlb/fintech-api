from typing import Dict

from bson import ObjectId
from api.db.database import database as db
from api.endpoints.exception_handler import exception_handler


loans = db.loans
users = db.users


def get_loan(loan_id: str) -> Dict:
    loan = loans.find_one({"_id": ObjectId(loan_id)})
    if loan:
        return loan
    else:
        raise exception_handler("404_NOT_FOUND")


def get_user(user_id: str) -> Dict:
    user = users.find_one({"_id": ObjectId(user_id)})
    if user:
        return user
    else:
        raise exception_handler("404_NOT_FOUND")
