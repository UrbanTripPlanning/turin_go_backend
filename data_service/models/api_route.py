from pydantic import BaseModel
from typing import Tuple, Optional


class SaveRoutePlanRequest(BaseModel):
    user_id: int
    start_at: Optional[int] = 0
    end_at: Optional[int] = 0
    src_loc: Tuple[float, float]
    dst_loc: Tuple[float, float]
    spend_time: int
    time_mode: int
