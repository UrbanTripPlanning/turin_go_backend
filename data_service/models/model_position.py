from pydantic import BaseModel


MODEL_NAME = "position"


class PositionModel(BaseModel):
    id: int
    lat: str  # Latitude
    lon: str  # Longitude
    name: str
    desc: str
