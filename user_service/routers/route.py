import httpx
from fastapi import APIRouter, Depends
from user_service.schemas import response
from utils.load import ROUTING_SERVICE_URL
from user_service.models.api_route import SearchRouteRequest


router = APIRouter()


@router.get("/search")
async def search(req: SearchRouteRequest = Depends()):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{ROUTING_SERVICE_URL}/route/search', params=req.dict())
    return response(resp.json())
