import asyncio
import pandas as pd
from data_service.database import get_mongo_collection


async def query():
    collection = get_mongo_collection("position")
    cursor = collection.find({})
    documents = []
    async for document in cursor:
        documents.append(document)
    return pd.DataFrame(documents)


def test():
    df = asyncio.run(query())
    print(df.head())
