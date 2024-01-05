import logging
from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from api.routers.utils.exception_handler import exception_handler
from api.models.token import create_token
from api.models.user import User
from core.config import SECRET, ALGORITHM
from passlib.context import CryptContext
from api.db.database import database
import os


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plane_password, hashed_password):
    return pwd_context.verify(plane_password, hashed_password)


async def authenticate_user(username: str, password: str):
    user = database.users.find_one({"username": username})

    if user and verify_password(password, user.get("hashed_password")):
        return User(**user)

    logging.warning(f"Failed authentication attempt for user: {username}")
    raise exception_handler("401_INVALID_CREDENTIALS")


def get_user_current(token: str = Depends(oauth2_scheme)):
    try:
        token_decode = jwt.decode(token, key=[SECRET], algorithms=[ALGORITHM])
        username = token_decode.get("sub")
        if username == None:
            exception_handler("401_INVALID_CREDENTIALS")
    except JWTError:
        raise exception_handler("401_INVALID_CREDENTIALS")

    user = database.users.find_one({"username": username})
    user["id"] = str(user["_id"])
    if not user:
        raise exception_handler("401_INVALID_CREDENTIALS")
    return User(**user)


def get_user_disabled_current(user: User = Depends(get_user_current)):
    if user.disabled:
        raise exception_handler("400_INACTIVE_USER")
    return user


def get_user_admin_current(user: User = Depends(get_user_current)):
    if user.role == "admin":
        return user
    else:
        raise exception_handler("403_NOT_ALLOWED")
