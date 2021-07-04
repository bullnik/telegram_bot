from typing import List
from place import PlaceToVisit
from road import TransportType


class UserRequest:
    def __init__(self, user_id: int,
                 possible_places_lists: List[List[PlaceToVisit]],
                 transport_types: List[TransportType],
                 with_baggage: bool,
                 is_favorite: bool = False):
        self.__user_id = user_id
        self.__possible_places_lists = possible_places_lists
        self.__transport_types = transport_types
        self.__with_baggage = with_baggage
        self.__is_favorite = is_favorite

    @property
    def is_favorite(self) -> int:
        return self.__is_favorite

    @property
    def user_id(self) -> int:
        return self.__user_id

    @property
    def possible_places_lists(self) -> List[List[PlaceToVisit]]:
        return self.__possible_places_lists

    @property
    def transport_types(self) -> List[TransportType]:
        return self.__transport_types

    @property
    def with_baggage(self) -> bool:
        return self.__with_baggage
