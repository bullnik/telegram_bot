from datetime import datetime
from enum import Enum


class TransportType(Enum):
    PLANE = "PLANE",
    TRAIN = "TRAIN",
    BUS = "BUS"


class Road:
    def __init__(self, transport_type: TransportType,
                 departure_town: str, arrival_town: str,
                 departure_time: datetime, arrival_time: datetime,
                 cost: int, baggage_cost: int,
                 link: str):
        self.__departure_town = departure_town
        self.__arrival_town = arrival_town
        self.__transport_type = transport_type
        self.__departure_time = departure_time
        self.__arrival_time = arrival_time
        self.__cost = cost
        self.__baggage_cost = baggage_cost
        self.__link = link

    @property
    def link(self) -> str:
        return self.__link

    @property
    def baggage_cost(self) -> int:
        return self.__baggage_cost

    @property
    def cost(self) -> int:
        return self.__cost

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
