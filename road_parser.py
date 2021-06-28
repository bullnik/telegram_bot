from abc import abstractmethod
from typing import List
from road import TransportType, Road


class RoadParser:
    @abstractmethod
    def parse_roads(self, transport_types: List[TransportType],
                    departure_town: str, arrival_town: str) -> List[Road]:
        raise NotImplemented()

    @abstractmethod
    def can_parse_transport(self, transport_type: TransportType) -> bool:
        raise NotImplemented()