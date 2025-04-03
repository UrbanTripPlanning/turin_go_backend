import httpx
import asyncio
import datetime
from typing import List
from fastapi import APIRouter, Depends, Query
from user_service.schemas import response
from utils.load import ROUTING_SERVICE_URL
from user_service.models.api_route import SearchRouteRequest


router = APIRouter()


async def get_search_request(
    start_at: int = 0,
    end_at: int = 0,
    src_loc: List[float] = Query(...),
    dst_loc: List[float] = Query(...)
) -> SearchRouteRequest:
    return SearchRouteRequest(
        start_at=start_at,
        end_at=end_at,
        src_loc=tuple(src_loc),
        dst_loc=tuple(dst_loc)
    )


@router.get("/search")
async def search(req: SearchRouteRequest = Depends(get_search_request)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{ROUTING_SERVICE_URL}/route/search', params=req.dict())
    return response(resp.json())


async def test_logic():
    start_at = int(datetime.datetime.now().timestamp())
    source_point = (7.705189, 45.068828)  # Departure point (longitude, latitude)
    target_point = (7.657668, 45.065126)  # Arrival point (longitude, latitude)
    req = SearchRouteRequest(start_at=start_at, src_loc=source_point, dst_loc=target_point)
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{ROUTING_SERVICE_URL}/route/search', params=req.dict())
    data = resp.json()
    print(data)


def test():
    asyncio.run(test_logic())
