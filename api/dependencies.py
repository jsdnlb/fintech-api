from typing import Dict

from bson import ObjectId
from api.db.database import database as db
from api.routers.utils.exception_handler import exception_handler


credit_line_db = db.credit_line
users = db.users


def get_credit_line(credit_line_id: str) -> Dict:
    credit_line = credit_line_db.find_one({"_id": ObjectId(credit_line_id)})
    if credit_line:
        return credit_line
    else:
        raise exception_handler("404_NOT_FOUND")


def get_user(user_id: str) -> Dict:
    user = users.find_one({"_id": ObjectId(user_id)})
    if user:
        return user
    else:
        raise exception_handler("404_NOT_FOUND")
