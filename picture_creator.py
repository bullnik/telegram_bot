from typing import List
from place import PlaceToVisit
from road import Road
import networkx as nx
import matplotlib.pyplot as plt
import random


class PictureCreator:
    @staticmethod
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

        w = 170 # задаем расположение
        h = 100
        pos = {}
        for i in range(len(possible_places_lists)):
            for j in range(len(possible_places_lists[i])):
                h0 = -((len(possible_places_lists[i])-1)*h)/2
                pos[possible_places_lists[i][j]] = (i*w, h0 + j*h)

        graph = nx.DiGraph()
        for route in routes:
            for pair in route:
                graph.add_edge(pair.departure_town, pair.arrival_town,
                               weight=pair.cost, title=str(pair.cost))

        # хз пригодится оно или нет, но пока тут остается
        edge_labels = nx.get_edge_attributes(graph, 'title')
        labels_edges = {}
        for route in routes:
            for pair in route:
                labels_edges[(pair.departure_town,
                              pair.arrival_town)] = str(pair.cost)

        plt.figure()

        nx.draw_networkx(graph, pos,
                         label='NetworkX',
                         width=1,
                         linewidths=1,
                         node_size=500,
                         node_color='orange',
                         alpha=0.9,
                         arrows=True)

        nx.draw_networkx_edge_labels(graph, pos,
                                     edge_labels=labels_edges,
                                     font_color='red',
                                     label_pos=0.75)

        name_fig = {'fig1.jpg', 'fig2.jpg', 'fig3.jpg', 'fig4.jpg'}

        plt.axis('off')
        plt.savefig(random.choice(name_fig))

        return ''

    @staticmethod
    def create_chart(stats: List[int]) -> str:
        # создать график популярности бота за последние n дней
        # лист - количество пользователей по последние дни
        # stats[0] - сегодня, stats[1] - вчера и т.д.

        return ''
