import httpx
import asyncio
import datetime
from typing import List
from fastapi import APIRouter, Depends, Query
from user_service.schemas import response
from utils.load import ROUTING_SERVICE_URL, DATA_SERVICE_URL
from user_service.models.api_route import SearchRouteRequest, SaveRoutePlanRequest


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


async def get_save_request(
    plan_id: str = '',
    user_id: str = '',
    start_at: int = 0,
    end_at: int = 0,
    src_loc: List[float] = Query(...),
    dst_loc: List[float] = Query(...),
    src_name: str = '',
    dst_name: str = '',
    spend_time: int = 0,
    time_mode: int = 0,
    route_mode: int = 0
) -> SaveRoutePlanRequest:
    return SaveRoutePlanRequest(
        plan_id=plan_id,
        user_id=user_id,
        start_at=start_at,
        end_at=end_at,
        src_loc=tuple(src_loc),
        dst_loc=tuple(dst_loc),
        src_name=src_name,
        dst_name=dst_name,
        spend_time=spend_time,
        time_mode=time_mode,
        route_mode=route_mode
    )


@router.get("/search")
async def search(req: SearchRouteRequest = Depends(get_search_request)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{ROUTING_SERVICE_URL}/route/search', params=req.dict())
    return response(resp.json())


@router.get("/save")
async def save(req: SaveRoutePlanRequest = Depends(get_save_request)):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/plan/save', params=req.dict())
    return response(resp.json())


@router.get("/list")
async def get_list(user_id: str):
    async with httpx.AsyncClient() as client:
        resp = await client.get(f'{DATA_SERVICE_URL}/plan/list', params={'user_id': user_id})
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
