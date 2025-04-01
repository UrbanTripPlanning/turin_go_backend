from enum import Enum


class Weather(int, Enum):
    CLEAR = 1
    RAIN = 2
    CLOUDS = 3
    SNOW = 4

    def name(self):
        return self._name_.lower()
