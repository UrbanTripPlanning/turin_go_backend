from pydantic import BaseModel
from typing import Tuple, Optional


class SearchRouteRequest(BaseModel):
    start_at: Optional[int] = 0  # timestamp
    end_at: Optional[int] = 0  # timestamp
    src_loc: Tuple[float, float]
    dst_loc: Tuple[float, float]
