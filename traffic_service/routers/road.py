from typing import Optional
from datetime import datetime
from fastapi import APIRouter
from traffic_service.services import road


router = APIRouter()
road_network = None


@router.get("/network")
async def network(start_time: Optional[datetime] = None, end_time: Optional[datetime] = None):
    global road_network
    if road_network is None:
        road_network = road.RoadNetwork(gnn_model='GCN')
    await road_network.async_init(start_time, end_time)
    return road_network.to_dict()
