from typing import List

import picture_creator
import route_creator
from settings import Settings
from answer import AnswerToUserRouteRequest
from database import Database
from request import UserRequest
from unfinished_request import UnfinishedRequest


class Controller:
    def __init__(self):
        self.__admin_password = 123
        self.__db = Database()
        self.__unfinished_requests = []
        self.__route_creator = route_creator.RouteCreator()
        self.__settings = Settings()

    def __load_request(self, user_id, request):
        self.clear_user_request(user_id)
        unfinished_request = UnfinishedRequest(user_id)
        unfinished_request.with_baggage = request.with_baggage
        unfinished_request.possible_places_lists = request.possible_places_lists
        unfinished_request.transport_types = request.transport_types
        unfinished_request.transport_types = request.is_favorite
        self.__unfinished_requests.append(unfinished_request)

    def load_last(self, user_id: int, num: int) -> bool:
        requests = self.__db.get_requests(user_id, num)
        if len(requests) > 0:
            request = requests[len(requests) - 1]
            self.__load_request(user_id, request)
            return True
        return False

    def load_favorite(self, user_id: int, num: int) -> bool:
        requests = self.__db.get_favorites_requests(user_id, num)
        if len(requests) > 0:
            request = requests[len(requests) - 1]
            self.__load_request(user_id, request)
            return True
        return False

    def get_answer_to_user_route_request(self, user_id: int) -> AnswerToUserRouteRequest:
        user_request = self.get_current_request(user_id)
        self.__db.insert_request(self.convert_to_finish_request(self.get_current_request(user_id)))
        routes = self.__route_creator.create_routes(user_request.possible_places_lists,
                                                    user_request.transport_types,
                                                    user_request.with_baggage)
        low_cost_route = self.__route_creator.get_low_cost_route(routes, user_request.with_baggage)
        answer = AnswerToUserRouteRequest(user_request.possible_places_lists,
                                          routes, low_cost_route)
        self.clear_user_request(user_id)
        return answer

    def clear_user_request(self, user_id: int):
        for request in self.__unfinished_requests:
            if request.user_id == user_id:
                self.__unfinished_requests.remove(request)

    @staticmethod
    def convert_to_finish_request(request: UnfinishedRequest):
        finish_request = UserRequest(request.user_id,
                                     request.possible_places_lists,
                                     request.transport_types,
                                     request.with_baggage,
                                     request.is_favorite)
        return finish_request

    def get_current_request(self, user_id: int) -> UnfinishedRequest:
        for request in self.__unfinished_requests:
            if request.user_id == user_id:
                return request
        request = UnfinishedRequest(user_id)
        self.__unfinished_requests.append(request)
        return request

    def get_settings(self) -> List[int]:
        return [self.__settings.get_max_stored_roads(), self.__settings.get_max_count_parsed_roads()]

    def get_favorites(self, user_id, requests_count: int) -> List[UserRequest]:
        try:
            user_id = int(user_id)
            return self.__db.get_favorites_requests(user_id, requests_count)
        except TypeError:
            return []

    def get_stats_picture(self, days_count: int) -> str:
        return picture_creator.PictureCreator.create_chart(self.__db.get_unique_users(days_count))

    def get_history(self, user_id, records_count: int) -> List[UserRequest]:
        try:
            user_id = int(user_id)
            return self.__db.get_requests(user_id, records_count)
        except TypeError:
            return []

    def get_admin_password(self):
        return self.__admin_password

    def get_max_count_parsed_roads(self) -> int:
        return self.__settings.get_max_count_parsed_roads()

    def get_max_saved_roads_count(self) -> int:
        return self.__settings.get_max_stored_roads()

    def set_max_count_parsed_roads(self, count) -> bool:
        try:
            count = int(count)
            self.__settings.set_max_count_parsed_roads(count)
            return True
        except ValueError:
            return False

    def set_max_saved_roads_count(self, count) -> bool:
        try:
            count = int(count)
            self.__settings.set_max_stored_roads(count)
            return True
        except ValueError:
            return False
