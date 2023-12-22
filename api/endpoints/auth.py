from datetime import timedelta
from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordRequestForm
from api.security.authentication import authenticate_user, create_token

router = APIRouter()

fake_users_db = {}


@router.post("/token")
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = authenticate_user(fake_users_db, form_data.username, form_data.password)
    access_token_expires = timedelta(minutes=30)
    access_token_jwt = create_token({"sub": user.username}, access_token_expires)
    return {"access_token": access_token_jwt, "token_type": "bearer"}
