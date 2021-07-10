from datetime import datetime, timedelta
from typing import List

from place import PlaceToVisit
from request import UserRequest
from road import TransportType, Road
import sqlite3


class Database:
    def __init__(self):
        try:
            database_file = open("database.sqlite")
            database_file.close()
        except IOError:
            self.__create_tables()

    def __create_tables(self):
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        cursor.executescript("""
            CREATE TABLE UserRequests
            (
                UserId INT,
                PossiblePlaces TEXT,
                TransportTypes TEXT,
                WithBaggage BOOLEAN,
                IsFavorite BOOLEAN,
                DateTime DATETIME
            );

            CREATE TABLE UniqueUsers
            (
                UserId INT,
                DateTime DATETIME
            );

            CREATE TABLE Roads 
            (
                DepartureTown TEXT,
                ArrivalTown TEXT,
                TransportType TEXT,
                DepartureTime DATETIME,
                ArrivalTime DATETIME,
                BaggageCost INT,
                Cost INT,
                Link TEXT
            );
        """)
        connection.commit()
        connection.close()

    def __str_to_datetime(self, string: str):
        return datetime(year=int(string[0:4]),
                        month=int(string[5:7]),
                        day=int(string[8:10]),
                        hour=int(string[11:13]),
                        minute=int(string[14:16]))

    def get_roads(self, departure_town: str, arrival_town: str,
                  transport_types: List[TransportType],
                  min_departure_time: datetime) -> List[Road]:
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        dep = departure_town.replace('\'', '')
        arr = arrival_town.replace('\'', '')
        min_time = str(min_departure_time)[0:19]
        max_time = str(min_departure_time + timedelta(hours=20))[0:19]
        roads = []
        for transport_type in transport_types:
            t_type = self.__transport_types_to_str([transport_type])
            cursor.execute(f"""
                SELECT * 
                FROM Roads
                WHERE DepartureTown = \'{dep}\'
                    AND ArrivalTown = \'{arr}\'
                    AND TransportType = \'{t_type}\'
            """)
            # AND
            # DepartureTime >= \'{min_time}\'
            # AND
            # DepartureTime <= \'{max_time}\'
            road_fetch = cursor.fetchall()
            if len(road_fetch) != 0:
                roads.append(road_fetch[0])
        output = []

        for road in roads:
            output.append(Road(departure_town=road[0],
                               arrival_town=road[1],
                               transport_type=self.__str_to_transport_types(road[2])[0],
                               departure_time=self.__str_to_datetime(road[3]),
                               arrival_time=self.__str_to_datetime(road[4]),
                               baggage_cost=road[5],
                               cost=road[6],
                               link=road[7]))
        connection.close()
        return output

    def insert_roads(self, roads: List[Road]):
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        for road in roads:
            link = road.link.replace('\'', '')
            departure_town = road.departure_town.replace('\'', '')
            arrival_town = road.arrival_town.replace('\'', '')
            cursor.execute(f"""
                INSERT INTO Roads (DepartureTown, ArrivalTown, TransportType, DepartureTime,
                                   ArrivalTime, BaggageCost, Cost, Link)
                SELECT \'{departure_town}\', \'{arrival_town}\', 
                        \'{self.__transport_types_to_str([road.transport_type])}\',
                        \'{str(road.departure_time)[:19]}\', \'{str(road.arrival_time)[:19]}\',
                        {road.baggage_cost}, {road.cost}, \'{link}\'
            """)
        connection.commit()
        connection.close()

    def insert_request(self, request: UserRequest):
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        user_id = request.user_id
        places = self.__possible_places_to_str(request.possible_places_lists)
        transport = self.__transport_types_to_str(request.transport_types)
        baggage = request.with_baggage
        is_favorite = request.is_favorite
        cursor.execute(f"""
            INSERT INTO UserRequests (UserId, PossiblePlaces, TransportTypes, WithBaggage, IsFavorite, DateTime)
            VALUES ({user_id}, \'{places}\', \'{transport}\', \'{baggage}\', \'{is_favorite}\', 
            \'{str(datetime.now())[0:16]}\');
        """)

        cursor.execute(f"""
            INSERT INTO UniqueUsers (UserId, DateTime)
            SELECT {user_id}, \'{str(datetime.now())[:16]}\'
            WHERE NOT EXISTS (SELECT 1
                              FROM UniqueUsers 
                              WHERE UserId = \'{user_id}\');
        """)
        connection.commit()
        connection.close()

    def __transport_types_to_str(self, transport_types: List[TransportType]) -> str:
        text = ''
        for transport_type in transport_types:
            if transport_type == TransportType.TRAIN:
                text += 'TRAIN '
            elif transport_type == TransportType.BUS:
                text += 'BUS '
            elif transport_type == TransportType.PLANE:
                text += 'PLANE '
        text = text[:-1]
        return text

    def __str_to_transport_types(self, text: str) -> List[TransportType]:
        transport_types = []
        for transport_type in text.split():
            if transport_type == 'TRAIN':
                transport_types.append(TransportType.TRAIN)
            elif transport_type == 'BUS':
                transport_types.append(TransportType.BUS)
            elif transport_type == 'PLANE':
                transport_types.append(TransportType.PLANE)
        return transport_types

    def __possible_places_to_str(self, possible_places_lists: List[List[PlaceToVisit]]):
        text = ''
        for places_list in possible_places_lists:
            for place in places_list:
                name = place.name.replace('/', '').replace('%', '').replace(';', '').replace('\'', '')
                text += name + '/' + str(place.min_stay_days) + '/' + str(place.max_stay_days)
                text += ';'
            text += '%'
        text = text[:-2]
        return text

    def __str_to_possible_places(self, text: str) -> List[List[PlaceToVisit]]:
        possible_places_lists = []
        for places_list_part in text.split('%'):
            places_list = []
            for place_part in places_list_part.split(';'):
                if place_part != '':
                    parts = place_part.split('/')
                    name = parts[0]
                    min_stay_days = int(parts[1])
                    max_stay_days = int(parts[2])
                    place = PlaceToVisit(name, min_stay_days, max_stay_days)
                    places_list.append(place)
            possible_places_lists.append(places_list)
        return possible_places_lists

    def __str_to_bool(self, text: str) -> bool:
        if text == 'False':
            return False
        if text == 'True':
            return True

    def get_requests(self, user_id: int, requests_count: int) -> List[UserRequest]:
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        output = []
        cursor.execute(f"""
            SELECT *
            FROM UserRequests 
            WHERE UserId = {user_id}
            ORDER BY DateTime DESC
            LIMIT {requests_count}
        """)
        requests = cursor.fetchall()
        for request in requests:
            output.append(UserRequest(user_id=request[0],
                                      possible_places_lists=self.__str_to_possible_places(request[1]),
                                      transport_types=self.__str_to_transport_types(request[2]),
                                      with_baggage=self.__str_to_bool(request[3]),
                                      is_favorite=self.__str_to_bool(request[4])))
        connection.close()
        return output

    def get_favorites_requests(self, user_id: int, num) -> List[UserRequest]:
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        cursor.execute(f"""
            SELECT *
            FROM UserRequests
            WHERE UserId = {user_id}
                AND IsFavorite = \'True\'
            ORDER BY DateTime DESC
            LIMIT {num}
        """)
        requests = cursor.fetchall()
        output = []
        for request in requests:
            output.append(UserRequest(user_id=request[0],
                                      possible_places_lists=self.__str_to_possible_places(request[1]),
                                      transport_types=self.__str_to_transport_types(request[2]),
                                      with_baggage=self.__str_to_bool(request[3]),
                                      is_favorite=self.__str_to_bool(request[4])))
        connection.close()
        return output

    def get_unique_users(self, last_days: int) -> List[int]:
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        unique_users = []
        for last_day in range(0, last_days + 1, 1):
            min_date = str(datetime.now() - timedelta(days=last_day + 1))[0:19]
            max_date = str(datetime.now() - timedelta(days=last_day))[0:19]
            cursor.execute(f"""
                SELECT count(*)
                FROM UniqueUsers
                WHERE DateTime > \'{min_date}\'
                    AND DateTime < \'{max_date}\'
            """)
            a = cursor.fetchall()
            unique_users.append(a[0])
        connection.close()
        return unique_users

    def get_usage_statistics(self, last_days: int) -> List[int]:
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        unique_users = []
        for last_day in range(0, last_days + 1, 1):
            min_date = str(datetime.now() - timedelta(days=last_day + 1))[0:19]
            max_date = str(datetime.now() - timedelta(days=last_day))[0:19]
            cursor.execute(f"""
                            SELECT count(*)
                            FROM UserRequests
                            WHERE DateTime > \'{min_date}\'
                                AND DateTime < \'{max_date}\'
                            """)
            a = cursor.fetchall()
            unique_users.append(a[0])
        connection.close()
        return unique_users
