from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return "Hi, what are u doing here?!"
