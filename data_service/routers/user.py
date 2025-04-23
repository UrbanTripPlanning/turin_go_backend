from utils.encrypt import md5_encrypt
from fastapi import APIRouter
from data_service.database import get_mongo_collection


router = APIRouter()


@router.get("/get")
async def get(username: str):
    user_collection = get_mongo_collection('user')
    user = await user_collection.find_one({'username': username})
    if user is None:
        return None

    return {
        'user_id': str(user['_id']),
        'username': user['username'],
        'password': user['password']
    }


@router.get("/insert")
async def insert(username: str, password: str):
    md5_password = md5_encrypt(password)

    user_collection = get_mongo_collection('user')
    data = {
        'username': username,
        'password': md5_password,
    }
    result = await user_collection.insert_one(data)

    return {
        'user_id': str(result.inserted_id),
        'username': username
    }
