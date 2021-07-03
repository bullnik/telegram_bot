from datetime import datetime
from typing import List
from request import UserRequest
from road import TransportType, Road


def init_database():

    # открыть базу и сделать там бим-бим бам-бам, чтобы остальные методы работали

    raise NotImplemented


def get_roads(departure_town: str, arrival_town: str,
              transport_types: List[TransportType],
              min_departure_time: datetime) -> List[Road]:

    # находит и возвращает дороги из базы по заданным параметрам

    return []


def insert_roads(roads: List[Road]):

    # вставляет дороги в базу

    raise NotImplemented


def insert_request(request: UserRequest):

    # вставляет запрос пользователя в базу
    # также надо записать пользователя в отдельную табличку с уникальными юзерами
    # В обоих случаях указывать еще дату запроса: datetime.now()

    raise NotImplemented


def get_requests(user_id: int, requests_count: int) -> List[UserRequest]:

    # возвращает n последних запросов пользователя из базы

    return []


def get_favorites_requests(user_id: int, requests_count) -> List[UserRequest]:

    # возвращает n последних избранных запросов

    return []


def get_unique_users(last_days: int) -> List[int]:

    # возвращает лист количества уникальных пользователей
    # list[0] -> сегодня, list[1] -> вчера и т.д.

    return []
