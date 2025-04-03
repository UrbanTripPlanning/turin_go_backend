from typing import List
from fastapi import APIRouter, Depends, Query
from routing_service.models.api_route import SearchRouteRequest
from routing_service.services import routing


router = APIRouter()


async def get_search_request(
    start_at: int = 0,
    end_at: int = 0,
    src_loc: List[float] = Query(...),
    dst_loc: List[float] = Query(...)
) -> SearchRouteRequest:
    return SearchRouteRequest(
        start_at=start_at,
        end_at=end_at,
        src_loc=tuple(src_loc),
        dst_loc=tuple(dst_loc)
    )


@router.get("/search")
async def search(req: SearchRouteRequest = Depends(get_search_request)):
    routes = await routing.history(req)
    return routes
