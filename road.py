from datetime import datetime
from enum import Enum


class TransportType(Enum):
    PLANE = "PLANE",
    TRAIN = "TRAIN",
    BUS = "BUS"


class Road:
    def __init__(self, transport_type: TransportType,
                 departure_town: str, arrival_town: str,
                 departure_time: datetime, arrival_time: datetime):
        self.__departure_town = departure_town
        self.__arrival_town = arrival_town
        self.__transport_type = transport_type
        self.__departure_time = departure_time
        self.__arrival_time = arrival_time

    @property
    def transport_type(self) -> TransportType:
        return self.__transport_type

    @property
    def departure_town(self) -> str:
        return self.__departure_town

    @property
    def arrival_town(self) -> str:
        return self.__arrival_town

    @property
    def departure_time(self) -> datetime:
        return self.__departure_time

    @property
    def arrival_time(self) -> datetime:
        return self.arrival_time
