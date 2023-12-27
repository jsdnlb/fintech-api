from typing import Optional, Union
from pydantic import BaseModel, validator
from passlib.context import CryptContext


pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


class User(BaseModel):
    username: Optional[str] = None
    age: Optional[int] = None
    role: Optional[str] = None
    full_name: Optional[Union[str, None]] = None
    email: Optional[Union[str, None]] = None
    hashed_password: Optional[str] = None
    disabled: Optional[Union[bool, None]] = None

    class Config:
        __collection__ = "users"
