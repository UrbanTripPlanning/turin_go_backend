from pydantic import BaseModel
from enums.weather import Weather


class SearchRouteRequest(BaseModel):
    timestamp: int
    start: str
    end: str
    weather: Weather
