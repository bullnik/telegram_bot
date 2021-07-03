from place import PlaceToVisit
from road import TransportType


class UnfinishedRequest:
    with_baggage = False
    possible_places_lists = None
    transport_types = None

    def __init__(self, user_id):
        self.__user_id = user_id
        self.possible_places_lists = [[]]
        self.transport_types = [TransportType.TRAIN, TransportType.BUS, TransportType.PLANE]
        self.with_baggage = False

    @property
    def user_id(self):
        return self.__user_id

    def add_town(self, number_in_list, town_name, min_days, max_days) -> bool:
        try:
            number_in_list = int(number_in_list)
            min_days = int(min_days)
            max_days = int(max_days)
            town_name = str(town_name)
        except TypeError:
            return False

        if min_days > max_days:
            return False

        if len(self.possible_places_lists) < number_in_list - 1:
            return False

        if len(self.possible_places_lists) == number_in_list - 1:
            self.possible_places_lists.append([])

        self.possible_places_lists[number_in_list - 1].append(PlaceToVisit(
            town_name, min_days, max_days))
        return True

    def remove_town(self, number_in_list, town_name) -> bool:
        try:
            number_in_list = int(number_in_list)
            town_name = str(town_name)
        except TypeError:
            return False

        if len(self.possible_places_lists) < number_in_list:
            return False

        is_town_deleted = False
        places = self.possible_places_lists[number_in_list - 1]
        for place in places:
            if place.name == town_name:
                places.remove(place)
                is_town_deleted = True

        for i in range(len(self.possible_places_lists) - 1, 0, -1):
            if len(self.possible_places_lists[i]) == 0:
                self.possible_places_lists.pop(i)
            else:
                break

        if is_town_deleted:
            return True
        return False

    def switch_train(self):
        try:
            self.transport_types.index(TransportType.TRAIN)
            self.transport_types.remove(TransportType.TRAIN)
        except ValueError:
            self.transport_types.append(TransportType.TRAIN)

    def switch_plane(self):
        try:
            self.transport_types.index(TransportType.PLANE)
            self.transport_types.remove(TransportType.PLANE)
        except ValueError:
            self.transport_types.append(TransportType.PLANE)

    def switch_bus(self):
        try:
            self.transport_types.index(TransportType.BUS)
            self.transport_types.remove(TransportType.BUS)
        except ValueError:
            self.transport_types.append(TransportType.BUS)
