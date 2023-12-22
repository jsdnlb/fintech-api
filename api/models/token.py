from typing import Union
from datetime import datetime, timedelta
from jose import jwt
from core.config import ALGORITHM
import os 

def create_token(data: dict, time_expire: Union[datetime, None] = None):
    data_copy = data.copy()
    if time_expire is None:
        expires = datetime.utcnow() + timedelta(minutes=15)
    else:
        expires = datetime.utcnow() + time_expire
    data_copy.update({"exp": expires})
    token_jwt = jwt.encode(data_copy, key=os.getenv("SECRET"), algorithm=ALGORITHM)

    return token_jwt
