from pydantic import BaseModel
from typing import Tuple


class SearchRouteRequest(BaseModel):
    start_at: int  # timestamp
    end_at: int  # timestamp
    src_loc: Tuple[float, float]
    dst_loc: Tuple[float, float]
