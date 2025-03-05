from fastapi import APIRouter
from enums.weather import Weather


router = APIRouter()


@router.get("/")
async def weather(timestamp: int):
    # TODO: get weather from db
    return {
        "weather": Weather.CLOUDS
    }

