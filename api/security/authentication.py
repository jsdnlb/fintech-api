import logging
from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
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
    raise HTTPException(
        status_code=401,
        detail="Incorrect username or password",
        headers={"WWW-Authenticate": "Bearer"},
    )


def get_user_current(token: str = Depends(oauth2_scheme)):
    try:
        token_decode = jwt.decode(token, key=[SECRET], algorithms=[ALGORITHM])
        username = token_decode.get("sub")
        if username == None:
            raise HTTPException(
                status_code=401,
                detail="Could not validate credentials",
                headers={"WWW-Authenticate": "Bearer"},
            )
    except JWTError:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user = database.users.find_one({"username": username})
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return User(**user)


def get_user_disabled_current(user: User = Depends(get_user_current)):
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
