import httpx
from fastapi import APIRouter
from user_service.schemas import response
from utils.load import DATA_SERVICE_URL


router = APIRouter()


@router.get("/search")
async def search(name: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/place/search?name={name}')
    return response(resp.json())


