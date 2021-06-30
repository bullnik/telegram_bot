from abc import abstractmethod
from datetime import datetime
from typing import List
from road import TransportType, Road


class RoadParser:
    def __init__(self):
        pass

    @abstractmethod
    def parse_roads(self, transport_types: List[TransportType],
                    departure_town: str, arrival_town: str,
                    min_departure_time: datetime) -> List[Road]:
        raise NotImplemented()

    @abstractmethod
    def can_parse_transport(self, transport_type: TransportType) -> bool:
        raise NotImplemented()
