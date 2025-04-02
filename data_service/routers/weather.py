import datetime
from fastapi import APIRouter
from enums.weather import Weather
from data_service.database import get_mongo_collection


router = APIRouter()


@router.get("/info")
async def weather():
    weather_collection = get_mongo_collection('weather_data')
    results = await weather_collection.find({}).to_list(length=None)
    return [convert(item) for item in results]


def convert(result):
    dt = datetime.datetime.strptime(result['date'], "%Y-%m-%d")
    dt = dt.replace(hour=result['hour'])
    return {
        'datetime': dt,
        'rain': 1 if result['condition'] == Weather.RAIN.value else 0,
        'weather_condition': result['desc'],
    }

