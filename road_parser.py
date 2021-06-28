from abc import abstractmethod


class RoadParser:
    @abstractmethod
    def parse_roads(self, transport_types) -> list:
        raise NotImplemented()

    @abstractmethod
    def can_parse_transport(self, transport_type) -> bool:
        raise NotImplemented()
