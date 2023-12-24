from fastapi import APIRouter, Depends, HTTPException
from api.models.user import User
from api.security.authentication import get_user_disabled_current
from api.db.database import database as db


router = APIRouter()
users = db.users


@router.get("/users/me")
def user(user: User = Depends(get_user_disabled_current)):
    return user


@router.post("/users/")
def create_user(user: User):
    print(user)
    result = users.insert_one(user.dict())
    if result.inserted_id:
        return {
            "message": "User created successfully",
            "user_id": str(result.inserted_id),
        }
    else:
        raise HTTPException(status_code=500, detail="Error creating user")


@router.get("/users/")
def get_all_users(user: User = Depends(get_user_disabled_current)):
    res = [x for x in users.find()]

    cleaned_users = [
        {**user, '_id': str(user['_id'])} for user in res
    ]

    return {
        "message": "List of users",
        "result": cleaned_users,
        "author" : user,
    }
