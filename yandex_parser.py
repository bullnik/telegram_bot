from abc import ABC
from road_parser import *
from road import *


class YandexParser(RoadParser, ABC):
    def parse_roads(self, transport_types: List[TransportType]) -> List[Road]:
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
