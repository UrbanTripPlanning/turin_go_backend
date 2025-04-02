import time
from fastapi import APIRouter
from traffic_service.services import traffic


router = APIRouter()


@router.get("/info")
async def info(timestamp: int):
    if timestamp <= int(time.time()):
        return await traffic.history_info(timestamp)
    else:
        return await traffic.predict_info(timestamp)
