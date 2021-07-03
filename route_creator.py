from datetime import datetime, timedelta
from typing import List
import database
from road import Road, TransportType
from place import PlaceToVisit
from test_parser import TestParser
from yandex_parser import YandexParser

parsers = [TestParser()]


def create_routes(possible_places_lists: List[List[PlaceToVisit]],
                  transport_types: List[TransportType],
                  with_baggage: bool) -> List[List[Road]]:
    if len(possible_places_lists) < 2:
        return []

    current_datetime = datetime.now()
    routes = []

    required_route_len = len(possible_places_lists) - 1

    recursive_traversal_places_and_adding_to_routes_list(possible_places_lists, transport_types,
                                                         with_baggage, routes, [], current_datetime)

    for route in routes:
        if len(route) < required_route_len:
            routes.remove(route)

    return routes


def get_low_cost_route(routes: List[List[Road]], with_baggage: bool) -> List[Road]:
    low_cost_route = []
    low_cost_route_cost = 9999999
    for route in routes:
        cost = 0
        for road in route:
            cost += get_total_price(road, with_baggage)
        if cost < low_cost_route_cost:
            low_cost_route = route
            low_cost_route_cost = cost
    return low_cost_route


def recursive_traversal_places_and_adding_to_routes_list(possible_places_lists: List[List[PlaceToVisit]],
                                                         transport_types: List[TransportType],
                                                         with_baggage: bool, routes: List[List[Road]],
                                                         current_route: List[Road],
                                                         current_datetime: datetime):
    if len(possible_places_lists) < 2:
        routes.append(current_route)
        return

    current_datetime += timedelta(hours=2)

    current_places_list = possible_places_lists[0]
    next_places_list = possible_places_lists[1]
    possible_places_lists.remove(current_places_list)

    for current_place in current_places_list:
        for next_place in next_places_list:
            for stay_days_count in range(current_place.min_stay_days, current_place.max_stay_days + 1):
                try:
                    road = get_road(current_place.name, next_place.name, transport_types,
                                    current_datetime, with_baggage)
                except FileNotFoundError:
                    continue

                route_copy = current_route.copy()
                route_copy.append(road)

                recursive_traversal_places_and_adding_to_routes_list(possible_places_lists, transport_types,
                                                                     with_baggage, routes, route_copy,
                                                                     current_datetime + timedelta(days=stay_days_count)
                                                                     + get_travel_time(road))


def get_travel_time(road: Road) -> timedelta:
    return road.arrival_time - road.departure_time


def get_road(departure_town: str, arrival_town: str,
             transport_types: List[TransportType],
             min_departure_time: datetime,
             with_baggage: bool) -> Road:
    all_founded_roads = []
    all_founded_roads.extend(database.get_roads(departure_town, arrival_town,
                                                transport_types, min_departure_time))
    if len(all_founded_roads) < 1:
        for parser in parsers:
            for transport_type in transport_types:
                if parser.can_parse_transport(transport_type):
                    roads = parser.parse_roads([transport_type], departure_town,
                                               arrival_town, min_departure_time)
                    all_founded_roads.extend(roads)

    if len(all_founded_roads) < 1:
        raise FileNotFoundError

    low_cost_road = get_low_cost_road(all_founded_roads, with_baggage)
    # database.insert_roads([low_cost_road])

    return low_cost_road


def get_low_cost_road(roads: List[Road], with_baggage: bool) -> Road:
    low_cost_road = roads[0]

    for road in roads:
        price = get_total_price(road, with_baggage)
        if price < get_total_price(low_cost_road, with_baggage):
            low_cost_road = road

    return low_cost_road


def get_total_price(road: Road, with_baggage: bool) -> int:
    total_price = road.cost

    if with_baggage:
        total_price += road.baggage_cost

    return total_price
