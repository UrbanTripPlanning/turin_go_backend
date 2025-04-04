from fastapi import APIRouter
from data_service.database import get_mongo_collection


router = APIRouter()


@router.get("/info")
async def position():
    traffic_collection = get_mongo_collection('position')
    results = await traffic_collection.find().to_list()
    return [convert(item) for item in results]


def convert(result):
    return {
        'node_id': result['node_id'],
        'coordinates': result['coordinates'],
    }
