from fastapi import Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from api.models.token import create_token
from api.models.user import User, UserInDB
from core.config import SECRET, ALGORITHM
from passlib.context import CryptContext
import os


fake_users_db = {}

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_user(db, username):
    if username in db:
        user_data = db[username]
        return UserInDB(**user_data)
    return []


def verify_password(plane_password, hashed_password):
    return pwd_context.verify(plane_password, hashed_password)


def authenticate_user(db, username, password):
    user = get_user(db, username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not verify_password(password, user.hashed_password):
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


def get_user_current(token: str = Depends(oauth2_scheme)):
    try:
        token_decode = jwt.decode(
            token, key=os.getenv("SECRET"), algorithms=[ALGORITHM]
        )
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

    user = get_user(fake_users_db, username)
    if not user:
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user


def get_user_disabled_current(user: User = Depends(get_user_current)):
    if user.disabled:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
