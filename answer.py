from typing import List

import picture_creator
from place import PlaceToVisit
from road import Road


class AnswerToUserRouteRequest:
    def __init__(self, possible_places_lists: List[List[PlaceToVisit]],
                 routes: List[List[Road]],
                 low_cost_route: List[Road]):
        self.__pic = picture_creator.PictureCreator.create_graph(possible_places_lists, routes, low_cost_route)
        self.__map = picture_creator.PictureCreator.create_map(possible_places_lists, routes, low_cost_route)
        self.__full_map = picture_creator.PictureCreator.create_full_map(possible_places_lists, routes, low_cost_route)
        self.__all_routes_count = len(routes)
        self.__low_cost_route = low_cost_route

    @property
    def map(self) -> str:
        return self.__map

    @property
    def full_map(self) -> str:
        return self.__full_map

    @property
    def pic(self) -> str:
        return self.__pic

    @property
    def all_routes_count(self) -> int:
        return self.__all_routes_count

    @property
    def low_cost_route(self) -> List[Road]:
        return self.__low_cost_route
