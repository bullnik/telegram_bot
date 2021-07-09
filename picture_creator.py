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
import plotly
from road_parser import TransportType
from selenium import webdriver


def test_data(possible_places_lists: List[List[PlaceToVisit]],
              routes: List[List[Road]],
              low_cost_route: List[Road]):
    possible_places_lists.clear()
    possible_places_lists.append([PlaceToVisit('Челябинск')])
    possible_places_lists.append([PlaceToVisit('Екатеринбург'), PlaceToVisit('Тюмень'), PlaceToVisit('Омск')])
    possible_places_lists.append([PlaceToVisit('Москва')])
    possible_places_lists.append([PlaceToVisit('Лондон'), PlaceToVisit('Париж')])
    possible_places_lists.append([PlaceToVisit('Рим')])
    possible_places_lists.append([PlaceToVisit('Вашингтон')])
    possible_places_lists.append([PlaceToVisit('Йоханнесбург')])
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
    routes.append([Road(TransportType.PLANE, 'Москва', 'Париж', datetime.datetime.now(), datetime.datetime.now(),
                        10000, 0, '')])
    routes.append([Road(TransportType.PLANE, 'Москва', 'Лондон', datetime.datetime.now(), datetime.datetime.now(),
                        14000, 0, '')])
    routes.append([Road(TransportType.PLANE, 'Лондон', 'Рим', datetime.datetime.now(), datetime.datetime.now(),
                        32000, 0, '')])
    routes.append([Road(TransportType.TRAIN, 'Париж', 'Рим', datetime.datetime.now(), datetime.datetime.now(),
                        30000, 0, '')])
    routes.append([Road(TransportType.BUS, 'Рим', 'Вашингтон', datetime.datetime.now(), datetime.datetime.now(),
                        60000, 0, '')])
    routes.append([Road(TransportType.BUS, 'Вашингтон', 'Йоханнесбург', datetime.datetime.now(), datetime.datetime.now(),
                        170000, 0, '')])

    low_cost_route.clear()
    low_cost_route.append(
        Road(TransportType.PLANE, 'Челябинск', 'Омск', datetime.datetime.now(), datetime.datetime.now(),
             2000, 500, ''))
    low_cost_route.append(
        Road(TransportType.PLANE, 'Омск', 'Москва', datetime.datetime.now(), datetime.datetime.now(),
             1700, 500, ''))
    low_cost_route.append(
        Road(TransportType.PLANE, 'Москва', 'Париж', datetime.datetime.now(), datetime.datetime.now(),
             10000, 0, ''))
    low_cost_route.append(
        Road(TransportType.TRAIN, 'Париж', 'Рим', datetime.datetime.now(), datetime.datetime.now(),
             30000, 0, ''))
    low_cost_route.append(
        Road(TransportType.BUS, 'Рим', 'Вашингтон', datetime.datetime.now(), datetime.datetime.now(),
             60000, 0, ''))
    low_cost_route.append(
        Road(TransportType.BUS, 'Вашингтон', 'Йоханнесбург', datetime.datetime.now(), datetime.datetime.now(),
             170000, 0, ''))


class PictureCreator:
    @staticmethod
    def create_graph(possible_places_lists: List[List[PlaceToVisit]],
                     routes: List[List[Road]],
                     low_cost_route: List[Road]) -> str:

        # test_data(possible_places_lists, routes, low_cost_route)

        w = 170  # задаем расположение
        h = 100

        pos = {}
        pair_list = []
        step = 0
        for i in range(len(possible_places_lists) - 1):
            for el1 in possible_places_lists[i]:
                for el2 in possible_places_lists[i + 1]:
                    route_found = False
                    transport = ' '
                    past_arrival_time = datetime.datetime.now()
                    for list_element in routes:
                        for road in list_element:
                            if el1.name == road.departure_town and el2.name == road.arrival_town:
                                delta = abs(road.departure_time - past_arrival_time)
                                if delta.days != 0:
                                    wait_time = str(delta.days)+'д'
                                else:
                                    wait_time = str(delta.seconds//3600)+'ч'
                                past_arrival_time = road.arrival_time
                                city1 = road.departure_town+'\n'+wait_time
                                city2 = road.arrival_town+'\n'+wait_time
                                total_cost = road.cost + road.baggage_cost
                                pos[city1] = ''

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
        pos[possible_places_lists[-1][0].name+'\n0ч'] = ''

        for i in range(len(possible_places_lists)):
            for j in range(len(possible_places_lists[i])):
                for key in pos.keys():
                    if key.find(possible_places_lists[i][j].name) != -1:
                        h0 = -((len(possible_places_lists[i]) - 1) * h) / 2
                        pos[key] = (i * w * 2, h0 + j * h)

        graph = nx.DiGraph()
        for pair in pair_list:
            graph.add_edge(pair[0], pair[1], weight=pair[2], title=str(pair[2]))

        graph_low_cost = nx.DiGraph()
        for road in low_cost_route:
            total_cost = road.cost + road.baggage_cost
            depar = road.departure_town
            arriv = road.arrival_town
            for key in pos.keys():
                if key.find(depar) != -1:
                    depar = key
                if key.find(arriv) != -1:
                    arriv = key
            graph_low_cost.add_edge(depar,
                                    arriv,
                                    weigth=total_cost,
                                    title=total_cost)

        labels_edges = {}
        for pair in pair_list:
            labels_edges[(pair[0], pair[1])] = str(pair[2]) + 'р. - ' + pair[3]

        plt.figure()

        # Рисует весь граф
        nx.draw_networkx(graph, pos,
                         label='NetworkX',
                         width=3,
                         linewidths=5,
                         node_size=5000,
                         node_color='orange',
                         alpha=0.9,
                         arrows=True)
        # Поверх основного графа рисует минимальную цену
        nx.draw_networkx(graph_low_cost, pos,
                         label='NetworkX',
                         width=8,
                         linewidths=5,
                         node_size=5000,
                         node_color='orange',
                         edge_color='green',
                         alpha=0.9,
                         arrows=True)
        nx.draw_networkx_edge_labels(graph_low_cost, pos,
                                     edge_labels=labels_edges,
                                     font_size=12,
                                     font_color='blue',
                                     label_pos=0.5)

        name_fig = ['fig1.jpg', 'fig2.jpg', 'fig3.jpg', 'fig4.jpg']

        plt.axis('off')
        file_name = random.choice(name_fig)
        img_path = getcwd() + '\\pictures\\' + file_name
        # plt.show()
        fig = plt.gcf()
        fig.set_size_inches((16, 9), forward=False)
        fig.savefig(img_path, dpi=150)
        plt.close()

        return img_path

    @staticmethod
    def create_map(possible_places_lists: List[List[PlaceToVisit]],
                   routes: List[List[Road]],
                   low_cost_route: List[Road]) -> str:

        # test_data(possible_places_lists, routes, low_cost_route)

        geolocator = Nominatim(user_agent="bot")
        city_coords = {}

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

        middle_longs = []
        middle_lats = []
        costs = []
        colors = []
        for i in range(len(possible_places_lists) - 1):
            for el1 in possible_places_lists[i]:
                for el2 in possible_places_lists[i + 1]:
                    for road in low_cost_route:
                        if el1.name == road.departure_town and el2.name == road.arrival_town:
                            transport_type = road.transport_type
                            city_names = [el1.name, el2.name]
                            city_from_coords = city_coords.get(el1.name)
                            city_to_coords = city_coords.get(el2.name)
                            middle_longs.append((city_from_coords[0] + city_to_coords[0])/2) # middle_long =
                            middle_lats.append((city_from_coords[1] + city_to_coords[1])/2) # middle_lat =
                            costs.append(str(road.cost + road.baggage_cost)+'р.') # cost =

                            map_line_color = 'blue'
                            if transport_type == TransportType.PLANE:
                                map_line_color = 'red'
                            elif transport_type == TransportType.TRAIN:
                                map_line_color = 'blue'
                            elif transport_type == TransportType.BUS:
                                map_line_color = 'green'
                            colors.append(map_line_color)

                            longitudes = [city_from_coords[0], city_to_coords[0]]
                            latitudes = [city_from_coords[1], city_to_coords[1]]
                            fig.add_trace(go.Scattermapbox(
                                mode="markers+text+lines",
                                lon=longitudes,
                                lat=latitudes,
                                text=city_names,
                                textposition='top right',
                                textfont=dict(size=15),
                                line={'color': map_line_color},
                                marker={'size': 14,
                                        'color': 'orange'}))
                            break

        fig.add_trace(go.Scattermapbox(
            mode="markers+text",
            lon=middle_longs,
            lat=middle_lats,
            text=costs,
            textposition='bottom right',
            textfont=dict(size=30),
            marker={'size': 5,
                    'color': colors}))

        center_long = (max_long + min_long) / 2
        center_lat = (max_lat + min_lat) / 2

        diff_long = abs(max_long - min_long)
        diff_lat = abs(max_lat - min_lat)
        map_zoom = 1
        if (diff_long/2) > diff_lat:
            if 270 <= diff_long < 360:
                map_zoom = 1.5
            elif 180 <= diff_long < 270:
                map_zoom = 2.1
            elif 90 <= diff_long < 180:
                map_zoom = 2.8
            elif 0 <= diff_long < 90:
                map_zoom = 3.5
        else:
            if 135 <= diff_lat < 180:
                map_zoom = 1.5
            elif 90 <= diff_lat < 135:
                map_zoom = 1.9
            elif 45 <= diff_lat < 90:
                map_zoom = 2.3
            elif 0 <= diff_lat < 45:
                map_zoom = 2.7

        token = 'pk.eyJ1IjoicXdlcnR5MTExcXdzenhjIiwiYSI6ImNrcXYxaWlsMjBhNG0yeG82dDZxaGg0ZmYifQ.sXb6HhGJc7fg98FBJfq18A'
        fig.update_layout(
            mapbox={
                'accesstoken': token,
                'center': {'lon': center_long, 'lat': center_lat},
                'style': "outdoors",
                'zoom': map_zoom},
            margin={'l': 0, 't': 0, 'b': 0, 'r': 0},
            showlegend=False)

        name_fig = ['map1', 'map2', 'map3', 'map4']
        file_name = random.choice(name_fig)
        html_path = getcwd() + '\\pictures\\' + file_name +'.html'
        plotly.offline.plot(fig, filename=html_path)

        driver = webdriver.Chrome(executable_path="chromedriver.exe")
        driver.maximize_window()
        driver.get('file://'+html_path)
        time.sleep(15)
        img_path = getcwd() + '\\pictures\\' + file_name + '.png'
        driver.save_screenshot(img_path)
        driver.quit()

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
        img_path = getcwd() + '\\pictures\\chart.jpg'
        plt.savefig(img_path)

        return img_path
