import datetime

from fastapi import APIRouter
from data_service.database import get_mongo_collection


router = APIRouter()


@router.get("/info")
async def info(timestamp: int):
    traffic_collection = get_mongo_collection('traffic_final')
    curr_dt = datetime.datetime.fromtimestamp(timestamp)
    results = await traffic_collection.find({
        'hour': curr_dt.hour,
        'week': curr_dt.weekday(),
        'month': curr_dt.month,
    }).to_list()
    return [convert(item) for item in results]


@router.get("/road/info")
async def road_info(timestamp: int):
    traffic_collection = get_mongo_collection('traffic_final')
    curr_dt = datetime.datetime.fromtimestamp(timestamp)
    pipeline = [
        {"$match": {
            'hour': curr_dt.hour,
            'week': curr_dt.weekday(),
            'month': curr_dt.month,
        }},
        {"$group": {
            "_id": "$road_id",
            "avg_speed_clear": {"$avg": "$speed_clear"},
            "avg_speed_rain": {"$avg": "$speed_rain"}
        }}
    ]
    results = await traffic_collection.aggregate(pipeline).to_list()
    return results


def convert(result):
    return {
        'road_id': result['road_id'],
        'head': result['head'],
        'tail': result['tail'],
        'hour': result['hour'],
        'speed_clear': result['speed_clear'],
        'speed_rain': result['speed_rain'],
    }
