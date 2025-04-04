from fastapi import APIRouter
from data_service.database import get_mongo_collection


router = APIRouter()


@router.get("/search")
async def search(name: str):
    query = {
        "$or": [
            {"name_it": {"$regex": f".*{name}.*", "$options": "i"}},
            {"name_en": {"$regex": f".*{name}.*", "$options": "i"}}
        ]
    }
    place_collection = get_mongo_collection('place')
    results = await place_collection.find(query).limit(10).to_list()
    return results
