import datetime

from fastapi import APIRouter
from data_service.database import get_mongo_collection


router = APIRouter()


@router.get("/info")
async def info():
    road_collection = get_mongo_collection('road')
    results = await road_collection.find({}).to_list(length=None)
    return [convert(item) for item in results]
    # return results


def convert(result):
    result['_id'] = str(result['_id'])
    return result
    # return {
    #     'road_id': result['road_id'],
    #     'head': result['head'],
    #     'tail': result['tail'],
    #     'hour': result['hour'],
    #     'speed': result['avg_speed'],
    # }
