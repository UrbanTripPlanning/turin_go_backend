from fastapi import APIRouter
from routing_service.models.api_route import SearchRouteRequest


router = APIRouter()


@router.get("/search")
async def search(req: SearchRouteRequest):
    # TODO: route generate logic
    # []{
    #   routes:[point1, point2, point3, ...],
    #   minutes: 20,
    #   distances: 1.4 (km),
    #   details: [...],
    #   _type: 0 (walk/car/...)
    # }, {...}
    return {}
