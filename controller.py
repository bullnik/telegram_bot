from typing import List

import database
import picture_creator
import settings
from database import init_database
from place import PlaceToVisit
from request import UserRequest
from road import TransportType
from unfinished_request import UnfinishedRequest

__admin_password = 123
#init_database()
unfinished_requests = []


def get_current_request(user_id: int) -> UnfinishedRequest:
    for request in unfinished_requests:
        if request.user_id == user_id:
            return request
    request = UnfinishedRequest(user_id)
    unfinished_requests.append(request)
    return request


def get_settings() -> List[int]:
    return [settings.get_max_stored_roads(), settings.get_max_count_parsed_roads()]


def get_favorites(user_id, requests_count: int) -> List[UserRequest]:
    try:
        user_id = int(user_id)
        return database.get_favorites_requests(user_id, requests_count)
    except TypeError:
        return []


def get_stats_picture(days_count: int) -> str:
    return picture_creator.create_chart(database.get_unique_users(days_count))


def get_history(user_id, records_count: int) -> List[UserRequest]:
    try:
        user_id = int(user_id)
        return database.get_requests(user_id, records_count)
    except TypeError:
        return []


def get_admin_password():
    return __admin_password


def get_max_count_parsed_roads() -> int:
    return settings.get_max_count_parsed_roads()


def get_max_saved_roads_count() -> int:
    return settings.get_max_stored_roads()


def set_max_count_parsed_roads(count) -> bool:
    try:
        count = int(count)
        settings.set_max_count_parsed_roads(count)
        return True
    except ValueError:
        return False


def set_max_saved_roads_count(count) -> bool:
    try:
        count = int(count)
        settings.set_max_count_parsed_roads(count)
        return True
    except ValueError:
        return False
