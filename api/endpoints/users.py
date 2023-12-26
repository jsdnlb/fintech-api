from bson import ObjectId
from fastapi import APIRouter, Depends, HTTPException
from passlib.context import CryptContext
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
    res = [x for x in users.find()]
    cleaned_users = [{**user, "_id": str(user["_id"])} for user in res]

    return {
        "message": "List of users",
        "result": cleaned_users,
        "author": user,
    }


@router.get("/users/{user_id}", response_model=User)
def get_user_by_id(
    user_id: str, current_user: User = Depends(get_user_disabled_current)
):
    user = users.find_one({"_id": ObjectId(user_id)})

    if user:
        user["_id"] = str(user["_id"])
        return user
    else:
        raise HTTPException(status_code=404, detail="User not found")


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
        raise HTTPException(status_code=500, detail="Error creating user")


@router.put("/users/{user_id}", response_model=User)
def update_user_by_id(
    user_id: str,
    user_update: User,
    current_user: User = Depends(get_user_disabled_current),
):
    object_id = ObjectId(user_id)
    hash = pwd_context.hash(user_update.hashed_password)
    user_data = user_update.dict(exclude_unset=True)
    user_data["hashed_password"] = hash

    result = users.update_one({"_id": object_id}, {"$set": user_data})

    if result.modified_count == 1:
        updated_user = users.find_one({"_id": object_id})
        updated_user["_id"] = str(updated_user["_id"])
        return updated_user
    elif result.matched_count == 0:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
    else:
        raise HTTPException(
            status_code=500, detail=f"Failed to update user with ID {user_id}"
        )


@router.delete("/users/{user_id}")
def delete_user_by_id(
    user_id: str, current_user: User = Depends(get_user_disabled_current)
):
    result = users.delete_one({"_id": ObjectId(user_id)})

    if result.deleted_count == 1:
        return {"message": f"User with ID {user_id} deleted successfully"}
    else:
        raise HTTPException(status_code=404, detail=f"User with ID {user_id} not found")
