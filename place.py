class PlaceToVisit:
    def __init__(self, name: str,
                 min_stay_days: int = 0,
                 max_stay_days: int = 0):
        self.__name = name
        self.__min_stay_days = min_stay_days
        self.__max_stay_days = max_stay_days

    @property
    def name(self):
        return self.__name

    @property
    def min_stay_days(self):
        return self.__min_stay_days

    @property
    def max_stay_days(self):
        return self.__max_stay_days
