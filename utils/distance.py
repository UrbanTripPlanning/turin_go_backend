import math
from functools import lru_cache
from typing import Tuple


@lru_cache(maxsize=None)
def euclidean_distance(p1: Tuple[float, float], p2: Tuple[float, float]) -> float:
    """
    Calculate the Euclidean distance between two points.

    :param p1: Tuple (x, y) representing the first point.
    :param p2: Tuple (x, y) representing the second point.
    :return: Euclidean distance.
    """
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])