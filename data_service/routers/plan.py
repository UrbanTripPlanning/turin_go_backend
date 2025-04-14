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
    spend_time: int = 0,
    time_mode: int = 0
) -> SaveRoutePlanRequest:
    return SaveRoutePlanRequest(
        user_id=user_id,
        start_at=start_at,
        end_at=end_at,
        src_loc=tuple(src_loc),
        dst_loc=tuple(dst_loc),
        spend_time=spend_time,
        time_mode=time_mode
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
        'spend_time': req.spend_time,
        'time_mode': req.time_mode,
    }
    _ = plan_collection.insert_one(data)
