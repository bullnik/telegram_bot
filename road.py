from enum import Enum


class Road:
    def __init__(self, transport_type,
                 departure_town, arrival_town,
                 departure_time, arrival_time):
        self.__departure_town = departure_town
        self.__arrival_town = arrival_town
        self.__transport_type = transport_type
        self.__departure_time = departure_time
        self.__arrival_time = arrival_time

    @property
    def transport_type(self):
        return self.__transport_type

    @property
    def departure_town(self):
        return self.__departure_town

    @property
    def arrival_town(self):
        return self.__arrival_town

    @property
    def departure_time(self):
        return self.__departure_time

    @property
    def arrival_time(self):
        return self.arrival_time


class TransportType(Enum):
    PLANE = "PLANE",
    TRAIN = "TRAIN",
    BUS = "BUS"
