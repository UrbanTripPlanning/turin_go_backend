from enum import Enum


class Weather(int, Enum):
    CLEAR = 1
    RAIN = 2
    CLOUDS = 3
    SNOW = 4
