import time
from fastapi import APIRouter
from traffic_service.services import road


router = APIRouter()


@router.get("/network")
async def network(start_time, end_time):
    road_network = road.RoadNetwork()
    await road_network.async_init(start_time, end_time)
    return road_network.to_dict()
