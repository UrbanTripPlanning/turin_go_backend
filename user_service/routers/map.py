import httpx
from fastapi import APIRouter
from user_service.schemas import response
from utils.load import DATA_SERVICE_URL, TRAFFIC_SERVICE_URL


router = APIRouter()


@router.get("/weather")
async def weather(timestamp: int):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/weather?timestamp={timestamp}')
    return response(resp.json())


@router.get("/info")
async def info(timestamp: int):
    # map info
    # position records
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/map_info?timestamp={timestamp}')
    return response(resp.json())


@router.get("/traffic")
async def traffic(timestamp: int):
    async with httpx.AsyncClient(timeout=30.0) as client:
        resp = await client.get(f'{TRAFFIC_SERVICE_URL}/traffic/info', params={'timestamp': timestamp})
    return response(resp.json())


