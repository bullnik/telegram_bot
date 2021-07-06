from typing import List
from place import PlaceToVisit
from road import Road
import networkx as nx
import matplotlib.pyplot as plt
import random
from os import getcwd


class PictureCreator:
    @staticmethod
    def create_graph(possible_places_lists: List[List[PlaceToVisit]],
                     routes: List[List[Road]],
                     low_cost_route: List[Road]) -> str:
        # нужно создать картинку, на которой будет нарисовано:
        # 1) города (possible_places_lists) с подписанными названиями
        # 2) проложены между ними пути (routes - это список путей от начального
        # города до конечного)
        # 3) жирным выделен самый дешевый путь (low_cost_route) (font_weight=bold)
        # хорошо, если цвета путей будут разными для разных типов транспорта
        # картинка должна сохраняться в папке pictures в проекте, а метод
        # возвращает путь к ней

        w = 170  # задаем расположение
        h = 100
        pos = {}
        for i in range(len(possible_places_lists)):
            for j in range(len(possible_places_lists[i])):
                h0 = -((len(possible_places_lists[i])-1)*h)/2
                pos[possible_places_lists[i][j].name] = (i*w, h0 + j*h)

        pair_list = []
        for i in range(len(possible_places_lists) - 1):
            for el1 in possible_places_lists[i]:
                for el2 in possible_places_lists[i + 1]:
                    city1 = None
                    city2 = None
                    total_cost = None
                    route_found = False
                    for list_element in routes:
                        for road in list_element:
                            if el1.name == road.departure_town and el2.name == road.arrival_town:
                                city1 = road.departure_town
                                city2 = road.arrival_town
                                total_cost = road.cost + road.baggage_cost
                                route_found = True
                                break
                        if route_found:
                            break
                    tuple_ = (city1, city2, total_cost)
                    pair_list.append(tuple_)

        graph = nx.DiGraph()
        for pair in pair_list:
            graph.add_edge(pair[0], pair[1], weight=pair[2], title=str(pair[2]))

        graph_low_cost = nx.DiGraph()
        for road in low_cost_route:
            total_cost = road.cost + road.baggage_cost
            graph_low_cost.add_edge(road.departure_town,
                                    road.arrival_town,
                                    weigth=total_cost,
                                    title=total_cost)

        labels_edges = {}
        for pair in pair_list:
            labels_edges[(pair[0], pair[1])] = str(pair[2])

        plt.figure()

        # Рисует весь граф
        nx.draw_networkx(graph, pos,
                         label='NetworkX',
                         width=3,
                         linewidths=5,
                         node_size=7000,
                         node_color='orange',
                         alpha=0.9,
                         arrows=True)

        nx.draw_networkx_labels(graph, pos, labels={node: node for node in graph.nodes()})
        nx.draw_networkx_edge_labels(graph, pos,
                                     edge_labels=labels_edges,
                                     font_size=14,
                                     font_color='red',
                                     label_pos=0.75)

        # Поверх основного графа рисует минимальную цену
        nx.draw_networkx(graph_low_cost, pos,
                         label='NetworkX',
                         width=3,
                         linewidths=5,
                         node_size=7000,
                         node_color='orange',
                         edge_color='green',
                         alpha=0.9,
                         arrows=True)
        nx.draw_networkx_edge_labels(graph_low_cost, pos,
                                     edge_labels=labels_edges,
                                     font_size=14,
                                     font_color='blue',
                                     label_pos=0.75)

        manager = plt.get_current_fig_manager()
        manager.window.showMaximized()

        name_fig = ['fig1.jpg', 'fig2.jpg', 'fig3.jpg', 'fig4.jpg']

        plt.axis('off')
        file_name = random.choice(name_fig)
        img_path = getcwd() + '\\pictures\\' + file_name
        plt.savefig(img_path)

        return img_path

    @staticmethod
    def create_chart(stats: List[int]) -> str:
        # создать график популярности бота за последние n дней
        # лист - количество пользователей по последние дни
        # stats[0] - сегодня, stats[1] - вчера и т.д.

        stats_by_date = stats[::-1]
        abscissa = list()

        for i in range(len(stats)):
            abscissa.append(i)

        plt.figure(figsize=(12, 7))

        plt.plot(abscissa, stats_by_date, 'o-r', alpha=0.7, lw=5, mec='b', mew=2, ms=10)
        plt.grid(True)
        plt.savefig('chart.jpg')

        return 'chart.jpg'
