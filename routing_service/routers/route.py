from fastapi import APIRouter, Depends
from routing_service.models.api_route import SearchRouteRequest
from routing_service.services import routing


router = APIRouter()


@router.get("/search")
async def search(req: SearchRouteRequest = Depends()):
    routes = await routing.history(req)
    return routes
