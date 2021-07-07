import datetime
import time
from typing import List
from place import PlaceToVisit
from road import Road
import networkx as nx
import matplotlib.pyplot as plt
import random
from os import getcwd
from geopy.geocoders import Nominatim
import plotly.graph_objects as go
from road_parser import TransportType


class PictureCreator:
    @staticmethod
    def create_graph(possible_places_lists: List[List[PlaceToVisit]],
                     routes: List[List[Road]],
                     low_cost_route: List[Road]) -> str:

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
                    transport = ' '
                    for list_element in routes:
                        for road in list_element:
                            if el1.name == road.departure_town and el2.name == road.arrival_town:
                                city1 = road.departure_town
                                city2 = road.arrival_town
                                total_cost = road.cost + road.baggage_cost
                                if road.transport_type == TransportType.PLANE:
                                    transport = 'Plane'
                                elif road.transport_type == TransportType.TRAIN:
                                    transport = 'Train'
                                elif road.transport_type == TransportType.BUS:
                                    transport = 'Bus'
                                route_found = True
                                tuple_ = (city1, city2, total_cost, transport)
                                pair_list.append(tuple_)
                                break
                        if route_found:
                            break

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
            labels_edges[(pair[0], pair[1])] = str(pair[2])+' - '+pair[3]

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
                                     label_pos=0.6)

        # Поверх основного графа рисует минимальную цену
        nx.draw_networkx(graph_low_cost, pos,
                         label='NetworkX',
                         width=6,
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
                                     label_pos=0.6)

        manager = plt.get_current_fig_manager()
        manager.window.showMaximized()
        time.sleep(1)

        name_fig = ['fig1.jpg', 'fig2.jpg', 'fig3.jpg', 'fig4.jpg']

        plt.axis('off')
        file_name = random.choice(name_fig)
        img_path = getcwd() + '\\pictures\\' + file_name
        plt.savefig(img_path)

        return img_path

    @staticmethod
    def create_map(possible_places_lists: List[List[PlaceToVisit]],
                   routes: List[List[Road]],
                   low_cost_route: List[Road]) -> str:
        '''
        possible_places_lists.clear()
        possible_places_lists.append([PlaceToVisit('Челябинск')])
        possible_places_lists.append([PlaceToVisit('Екатеринбург'), PlaceToVisit('Тюмень'), PlaceToVisit('Омск')])
        possible_places_lists.append([PlaceToVisit('Москва')])
        routes.clear()
        routes.append([Road(TransportType.TRAIN, 'Челябинск', 'Екатеринбург', datetime.datetime.now(),
                            datetime.datetime.now(), 1200, 0, ''),
                       Road(TransportType.BUS, 'Челябинск', 'Екатеринбург', datetime.datetime.now(),
                            datetime.datetime.now(), 600, 0, '')])
        routes.append([Road(TransportType.TRAIN, 'Челябинск', 'Тюмень', datetime.datetime.now(),
                            datetime.datetime.now(), 800, 0, '')])
        routes.append([Road(TransportType.PLANE, 'Челябинск', 'Омск', datetime.datetime.now(), datetime.datetime.now(),
                            2000, 500, '')])
        routes.append([Road(TransportType.PLANE, 'Омск', 'Москва', datetime.datetime.now(), datetime.datetime.now(),
                            1700, 500, '')])
        routes.append([Road(TransportType.PLANE, 'Екатеринбург', 'Москва', datetime.datetime.now(),
                            datetime.datetime.now(), 4000, 500, ''),
                       Road(TransportType.PLANE, 'Екатеринбург', 'Москва', datetime.datetime.now(),
                            datetime.datetime.now(), 4700, 700, '')])
        routes.append([Road(TransportType.PLANE, 'Тюмень', 'Москва', datetime.datetime.now(), datetime.datetime.now(),
                            6800, 400, '')])

        low_cost_route.clear()
        low_cost_route.append(
            Road(TransportType.BUS, 'Челябинск', 'Екатеринбург', datetime.datetime.now(), datetime.datetime.now(), 600,
                 0, ''))
        low_cost_route.append(
            Road(TransportType.PLANE, 'Екатеринбург', 'Москва', datetime.datetime.now(), datetime.datetime.now(), 4000,
                 500, ''))
        '''

        geolocator = Nominatim(user_agent="bot")
        city_coords = {}
        # city_names = []
        # longitudes = []
        # latitudes = []
        # #locations = []

        loc = geolocator.geocode(query=possible_places_lists[0][0].name, language='ru_RU')
        min_long = loc.longitude
        max_long = loc.longitude
        min_lat = loc.latitude
        max_lat = loc.latitude
        for element in possible_places_lists:
            for city in element:
                loc = geolocator.geocode(query=city.name, language='ru_RU')
                city_coords[city.name] = (loc.longitude, loc.latitude)
                # находим минимум и максимум долготы
                if min_long > loc.longitude:
                    min_long = loc.longitude
                elif max_long < loc.longitude:
                    max_long = loc.longitude
                    # находим минимум и максимум широты
                if min_lat > loc.latitude:
                    min_lat = loc.latitude
                elif max_lat < loc.latitude:
                    max_lat = loc.latitude

        fig = go.Figure()

        for i in range(len(possible_places_lists) - 1):
            for el1 in possible_places_lists[i]:
                for el2 in possible_places_lists[i + 1]:
                    for road in low_cost_route:
                        if el1.name == road.departure_town and el2.name == road.arrival_town:
                            transport_type = road.transport_type
                            city_names = [el1.name, el2.name]
                            city_from_coords = city_coords.get(el1.name)
                            city_to_coords = city_coords.get(el2.name)

                            map_line_color = 'blue'
                            if transport_type == TransportType.PLANE:
                                map_line_color = 'red'
                            elif transport_type == TransportType.TRAIN:
                                map_line_color = 'blue'
                            elif transport_type == TransportType.BUS:
                                map_line_color = 'green'

                            longitudes = [city_from_coords[0], city_to_coords[0]]
                            latitudes = [city_from_coords[1], city_to_coords[1]]
                            fig.add_trace(go.Scattermapbox(
                                showlegend=False,
                                mode='markers+lines',
                                lon=longitudes,
                                lat=latitudes,
                                text=city_names,
                                line={'color': map_line_color},
                                marker={'size': 20,
                                        'color': 'blue'}))
                            break

        fig.update_layout(
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            mapbox={
                'center': {'lon': (max_long + min_long) / 2, 'lat': (max_lat + min_lat) / 2},
                'style': "stamen-terrain",
                'zoom': 3})

        # fig.show()

        name_fig = ['map1.jpeg', 'map2.jpeg', 'map3.jpeg', 'map4.jpeg']
        file_name = random.choice(name_fig)
        img_path = getcwd() + '\\pictures\\' + file_name
        fig.write_image(img_path)

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
