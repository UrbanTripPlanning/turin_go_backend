import time
from fastapi import APIRouter
from traffic_service.services import history, predict


router = APIRouter()


@router.get("/info")
async def info(timestamp: int):
    if timestamp <= int(time.time()):
        return await history.traffic_data(timestamp)
    else:
        return await predict.traffic_data(timestamp)
