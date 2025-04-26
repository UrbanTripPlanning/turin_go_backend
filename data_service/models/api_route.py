from pydantic import BaseModel
from typing import Tuple, Optional


class SaveRoutePlanRequest(BaseModel):
    plan_id: Optional[str] = ''
    user_id: str
    start_at: Optional[int] = 0
    end_at: Optional[int] = 0
    src_loc: Tuple[float, float]
    dst_loc: Tuple[float, float]
    src_name: str
    dst_name: str
    spend_time: int
    time_mode: int
    route_mode: int
