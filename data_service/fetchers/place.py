import asyncio
import pandas as pd
from data_service.database import get_mongo_collection


def load_csv(file_path):
    return pd.read_csv(file_path)


async def fetch_from_local():
    place_path = '../data/enriched_landmarks.csv'
    place_df = load_csv(place_path)
    place_data = place_df.rename(columns={'Italian Name': 'name_it', 'English Name': 'name_en'}).to_dict('records')
    place_collection = get_mongo_collection('place')
    for data in place_data:
        _ = await place_collection.update_one({"name_en": data['name_en']},
                                              {"$set": data}, upsert=True)


def test():
    asyncio.run(fetch_from_local())

