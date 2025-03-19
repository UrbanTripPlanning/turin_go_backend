import datetime

from fastapi import APIRouter
from data_service.database import get_mongo_collection


router = APIRouter()


@router.get("/info")
async def traffic(timestamp: int):
    traffic_collection = get_mongo_collection('traffic')
    curr_dt = datetime.datetime.fromtimestamp(timestamp)
    # date = curr_dt.strftime('%Y-%m-%d')
    hour = curr_dt.hour
    results = await traffic_collection.find({'hour': hour}).to_list()
    return [convert(item) for item in results]


def convert(result):
    return {
        'road_id': result['road_id'],
        'head': result['head'],
        'tail': result['tail'],
        'hour': result['hour'],
        'speed': result['avg_speed'],
    }
