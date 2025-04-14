from typing import List
from fastapi import APIRouter, Depends, Query
from data_service.database import get_mongo_collection
from data_service.models.api_route import SaveRoutePlanRequest


router = APIRouter()


async def get_save_request(
    user_id: int = 0,
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


@router.get("/save")
async def save(req: SaveRoutePlanRequest = Depends(get_save_request)):
    plan_collection = get_mongo_collection('plan')
    data = {
        'user_id': req.user_id,
        'start_at': req.start_at,
        'end_at': req.end_at,
        'src_loc': req.src_loc,
        'dst_loc': req.dst_loc,
        'src_name': req.src_name,
        'dst_name': req.dst_name,
        'spend_time': req.spend_time,
        'time_mode': req.time_mode,
        'route_mode': req.route_mode
    }
    _ = plan_collection.insert_one(data)


@router.get("/list")
async def get_list(user_id: int):
    plan_collection = get_mongo_collection('plan')
    results = await plan_collection.find({'user_id': user_id}).to_list()
    return [convert(item) for item in results]


def convert(result):
    return {
        'user_id': result['user_id'],
        'start_at': result['start_at'],
        'end_at': result['end_at'],
        'src_loc': result['src_loc'],
        'dst_loc': result['dst_loc'],
        'src_name': result['src_name'],
        'dst_name': result['dst_name'],
        'spend_time': result['spend_time'],
        'time_mode': result['time_mode'],
        'route_mode': result['route_mode'],
    }
