from typing import Union
from pydantic import BaseModel


class User(BaseModel):
    username: str
    full_name: Union[str, None] = None
    email: Union[str, None] = None
    disabled: Union[bool, None] = None


class UserInDB(User):
    hashed_password: str
