from typing import Optional, Union
from pydantic import BaseModel


class User(BaseModel):
    id: Optional[str] = None
    username: Optional[str] = None
    age: Optional[int] = None
    role: Optional[str] = None
    full_name: Optional[Union[str, None]] = None
    email: Optional[Union[str, None]] = None
    hashed_password: Optional[str] = None
    disabled: Optional[Union[bool, None]] = None

    class Config:
        __collection__ = "users"
