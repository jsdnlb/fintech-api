from fastapi import APIRouter, Depends, HTTPException
from api.models.user import User
from api.security.authentication import get_user_disabled_current

router = APIRouter()


@router.get("/users/me")
def user(user: User = Depends(get_user_disabled_current)):
    return user
