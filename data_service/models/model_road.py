from pydantic import BaseModel


MODEL_NAME = "road"


class RoadModel(BaseModel):
    id: int
    start_id: int  # position_id
    end_id: int  # position_id
    distance: int
    flow: int
    speed: int
    timestamp: str
