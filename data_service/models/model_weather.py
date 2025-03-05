from pydantic import BaseModel
from enums.weather import Weather


MODEL_NAME = "weather"


class WeatherModel(BaseModel):
    id: int
    mode: Weather
    label: str
    date: str
    hour: int
    city: str
