from typing import List
from bson import ObjectId
from fastapi import APIRouter, Body, Depends
from passlib.context import CryptContext
from api.routers.utils.exception_handler import exception_handler
from api.models.user import User
from api.security.authentication import get_user_disabled_current
from api.db.database import database as db


router = APIRouter()
users = db.users
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


@router.get("/users/me")
def user(user: User = Depends(get_user_disabled_current)):
    return user


@router.get("/users/")
def get_all_users(user: User = Depends(get_user_disabled_current)):
    all_records = [x for x in users.find()]

    cleaned_users = [{**user, "_id": str(user["_id"])} for user in all_records]
    user_ids = [str(user["_id"]) for user in all_records]
    return {
        "message": "List of users",
        "users_ids": user_ids,
        "result": cleaned_users,
    }


@router.get("/users/{user_id}", response_model=User)
def get_user_by_id(
    user_id: str, current_user: User = Depends(get_user_disabled_current)
):
    user = users.find_one({"_id": ObjectId(user_id)})

    if user:
        user["id"] = str(user["_id"])
        return user
    else:
        raise exception_handler("404_NOT_FOUND")


@router.post("/users/")
def create_user(user: User, current_user: User = Depends(get_user_disabled_current)):
    hash = pwd_context.hash(user.hashed_password)
    user_data = user.__dict__
    user_data["hashed_password"] = hash
    result = users.insert_one(user_data)
    if result.inserted_id:
        return {
            "message": "User created successfully",
            "user_id": str(result.inserted_id),
        }
    else:
        raise exception_handler("500_CREATE")


@router.put("/users/{user_id}", response_model=dict)
def update_user(
    user_id: str,
    user_data: User,
    current_user: User = Depends(get_user_disabled_current),
):
    obj_id = ObjectId(user_id)
    existing_user = users.find_one({"_id": obj_id})

    if existing_user is None:
        raise exception_handler("404_NOT_FOUND")

    for field, value in user_data.dict(exclude_unset=True).items():
        if field == "hashed_password":
            if value:
                value = pwd_context.hash(value)
            else:
                value = existing_user.get("hashed_password", None)

        existing_user[field] = value

    result = users.update_one({"_id": obj_id}, {"$set": existing_user})
    existing_user["_id"] = str(existing_user["_id"])

    if result.modified_count == 1:
        return {
            "message": "User updated successfully",
            "data": existing_user,
        }
    elif result.modified_count == 0:
        raise exception_handler("422_UNPROCESSABLE_ENTITY")
    else:
        raise exception_handler("500_UPDATE")


@router.delete("/users/{user_id}")
def delete_user_by_id(
    user_id: str, current_user: User = Depends(get_user_disabled_current)
):
    result = users.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 1:
        return {"message": f"User with ID {user_id} deleted successfully"}
    else:
        raise exception_handler("404_NOT_FOUND")


@router.delete("/users/")
def delete_users(
    user: User = Depends(get_user_disabled_current),
    ids: List[str] = Body(..., required=True),
):
    if not ids:
        raise exception_handler("422_NO_ID")

    object_ids = [ObjectId(id) for id in ids]
    deleted_count = users.delete_many({"_id": {"$in": object_ids}})

    if deleted_count.deleted_count == 0:
        raise exception_handler("404_NOT_FOUND")

    return {
        "message": "Users deleted",
        "deleted_count": deleted_count.deleted_count,
    }
