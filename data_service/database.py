import os
from dotenv import load_dotenv
from motor.motor_asyncio import AsyncIOMotorClient


load_dotenv()


MONGO_URI = os.getenv("MONGODB_URL")
MONGO_DB_NAME = 'turin_go'
mongo_client = AsyncIOMotorClient(MONGO_URI)
mongo_db = mongo_client[MONGO_DB_NAME]


def get_mongo_collection(collection_name: str):
    return mongo_db[collection_name]
