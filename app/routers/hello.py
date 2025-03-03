from fastapi import APIRouter
from app.schemas import response


router = APIRouter()


@router.get("/")
def say_hello(msg: str):
    if msg == '123':
        return response({"payload": "1234"})
    else:
        return response({}, 500, "msg unmatched")
