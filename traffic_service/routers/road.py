from typing import Optional
from fastapi import APIRouter
from traffic_service.services import road


router = APIRouter()
road_network = None


@router.get("/network")
async def network(timestamp: Optional[int] = None):
    global road_network
    if road_network is None:
        road_network = road.RoadNetwork(gnn_model='GCN')
    await road_network.async_init(timestamp)
    return road_network.to_dict()
