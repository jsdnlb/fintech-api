from typing import Union
from pydantic import BaseModel


class User(BaseModel):
    username: str
    age: int
    role: str
    full_name: Union[str, None] = None
    email: Union[str, None] = None
    hashed_password: str
    disabled: Union[bool, None] = None

    class Config:
        __collection__ = "users"
