from typing import List
from place import PlaceToVisit
from road import Road


def create_graph(possible_places_lists: List[List[PlaceToVisit]],
                   routes: List[List[Road]],
                   low_cost_route: List[Road]) -> str:

    # нужно создать картинку, на которой будет нарисовано:
    # 1) города (possible_places_lists) с подписанными названиями
    # 2) проложены между ними пути (routes - это список путей от начального
    # города до конечного)
    # 3) жирным выделен самый дешевый путь (low_cost_route)
    # хорошо, если цвета путей будут разными для разных типов транспорта
    # картинка должна сохраняться в папке pictures в проекте, а метод
    # возвращает путь к ней

    raise NotImplemented


def create_chart(stats: List[int]) -> str:

    # создать график популярности бота за последние n дней
    # лист - количество пользователей по последние дни
    # stats[0] - сегодня, stats[1] - вчера и т.д.

    raise NotImplemented
