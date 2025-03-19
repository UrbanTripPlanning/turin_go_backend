from pydantic import BaseModel


class SearchRouteRequest(BaseModel):
    timestamp: int
    start: str
    end: str


