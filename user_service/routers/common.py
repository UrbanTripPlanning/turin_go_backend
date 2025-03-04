import httpx
from fastapi import APIRouter
from user_service.schemas import response
from utils.load import DATA_SERVICE_URL


router = APIRouter()


@router.get("/user")
async def user_info(user_id: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/user/{user_id}')
    return response(resp.json())
