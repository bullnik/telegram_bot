from abc import ABC
from road_parser import *
from road import *


class YandexParser(RoadParser, ABC):
    def __init__(self):
        super().__init__()

    def parse_roads(self, transport_types: List[TransportType],
                    departure_town: str, arrival_town: str,
                    min_departure_time: datetime) -> List[Road]:

        # возвращает список дорог, спаршенных с сайта
        # время отправления: от min_departure_time до конца дня

        raise NotImplemented()

    def can_parse_transport(self, transport_type: TransportType) -> bool:
        if transport_type == TransportType.PLANE:
            return False
        elif transport_type == TransportType.TRAIN:
            return False
        elif transport_type == TransportType.BUS:
            return False
        else:
            raise NotImplemented()
