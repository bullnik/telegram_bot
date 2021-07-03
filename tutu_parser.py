import datetime
import time
from abc import ABC
from road_parser import *
from road import *
from selenium import webdriver
import selenium.common.exceptions
import settings

CHROME_EXE_PATH = "chromedriver.exe"
MAX_COUNT_TICKETS_FOR_PARSING = settings.get_max_count_parsed_roads()


def parse_avia_tickets(departure_town: str, arrival_town: str, min_departure_time: datetime):
    driver = webdriver.Chrome(CHROME_EXE_PATH)
    driver.set_window_size(1500, 1000)
    driver.get("https://avia.tutu.ru/")

    departure = driver.find_element_by_xpath("//input[@class='o33560 o33576']")
    print(departure)  # проверка
    departure.send_keys(departure_town)
    time.sleep(1)

    arrival = driver.find_element_by_xpath("//input[@class='o33560 o33641']")
    print(arrival)  # для проверки что всё норм в консоль пишется элемент
    arrival.send_keys(arrival_town)  # тут будет подставляться город Куда
    time.sleep(1)

    print("Откуда: " + departure.get_attribute('value'))  # Проверяю что всё правильно подставилось в поля
    print("Куда: " + arrival.get_attribute('value'))  #

    date_block = driver.find_element_by_xpath("//input[@class='o33560 o33663 o33658 o33659']")
    print(date_block)
    date_block.send_keys(min_departure_time.strftime('%d.%m.%Y'))
    time.sleep(0.3)

    search_button = driver.find_element_by_xpath("//button[@class='order-group-element o33688 o33693 o33695']")
    search_button.click()

    time.sleep(10)

    found_tickets_count = int(driver.find_element_by_xpath("//span[@class='o33124 o338 o3330 o3363']")
                              .find_elements_by_xpath(".//*")[0]
                              .find_elements_by_xpath(".//*")[0]
                              .text.split(' ')[0])
    max_for_parsing = found_tickets_count if found_tickets_count <= MAX_COUNT_TICKETS_FOR_PARSING else MAX_COUNT_TICKETS_FOR_PARSING
    print("Всего будем парсить: " + str(max_for_parsing))
    tickets = []
    i = 0
    while i < max_for_parsing:
        for step in range(0, 10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5)
        tickets = driver.find_elements_by_xpath("//div[@class='_3myc0zS07d6p2suflgjuDQ']")
        i = len(tickets)
        print('значение i: ' + str(i))
        print('значение max_for_parsing: ' + str(max_for_parsing))
        print('Бесконечный цикл?')

    print("Билетов всего: " + str(len(tickets)))
    print("Будем парсить: " + str(max_for_parsing))

    roads = []
    for j in range(0, max_for_parsing):
        if tickets[j].find_element_by_xpath(".//span[@data-ti='route_main_line']").text != 'Прямой':
            continue
        transport_type = TransportType.PLANE
        tickets_times = tickets[j].find_elements_by_xpath(".//span[@class='o33733']")
        ticket_departure_time = tickets_times[0].text.split(':')
        departure_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                    min_departure_time.year,
                                    min_departure_time.month,
                                    min_departure_time.day,
                                    ticket_departure_time[0],
                                    ticket_departure_time[1],
                                    '00')
        departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

        ticket_arrival_time = tickets_times[1].text.split(':')
        day = min_departure_time.day
        # часы приезда < часы выезда => прибыл в следующий день
        if int(ticket_arrival_time[0]) <= int(ticket_departure_time[0]):
            day = min_departure_time.day + 1
        arrival_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                  min_departure_time.year,
                                  min_departure_time.month,
                                  day,
                                  ticket_arrival_time[0],
                                  ticket_arrival_time[1],
                                  '00')
        arrival_time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')

        cost = ''
        for i in str(tickets[j].find_element_by_xpath(".//span[@data-ti='price']").text):
            if i.isdigit():
                cost += i
        cost = int(cost)

        link = driver.current_url
        baggage_cost = 0

        print('transport_type: ' + 'PLANE')
        print('departure_town: ' + departure_town)
        print('arrival_town: ' + arrival_town)
        print('departure_time: ' + str(departure_time))
        print('arrival_time: ' + str(arrival_time))
        print('cost: ' + str(cost))
        print('baggage_cost: ' + str(baggage_cost))
        print('link: ' + link)
        road = Road(transport_type=transport_type,
                    departure_town=departure_town,
                    arrival_town=arrival_town,
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    cost=cost,
                    baggage_cost=baggage_cost,
                    link=link
                    )
        roads.append(road)
    driver.quit()
    return roads


def parse_train_tickets(departure_town: str, arrival_town: str, min_departure_time: datetime):
    driver = webdriver.Chrome(CHROME_EXE_PATH)
    driver.set_window_size(1500, 1000)
    driver.get("https://www.tutu.ru/poezda/")

    departure = driver.find_element_by_xpath("//input[@class='input_field j-station_input  j-station_input_from']")
    print(departure)  # проверка
    departure.send_keys(departure_town)
    time.sleep(1)

    arrival = driver.find_element_by_xpath("//input[@class='input_field j-station_input  j-station_input_to']")
    print(arrival)  # для проверки что всё норм в консоль пишется элемент
    arrival.send_keys(arrival_town)  # тут будет подставляться город Куда
    time.sleep(1)

    print("Откуда: " + departure.get_attribute('value'))  # Проверяю что всё правильно подставилось в поля
    print("Куда: " + arrival.get_attribute('value'))  #

    date_block = driver.find_element_by_xpath("//input[@class='input_field j-permanent_open j-input j-date_to']")
    print(date_block)
    date_block.send_keys(min_departure_time.strftime('%d.%m.%Y'))
    time.sleep(1)

    search_button = driver.find_element_by_xpath("//button[@class='b-button__arrow__button j-button j-button-submit _title j-submit_button _blue']")
    search_button.click()

    time.sleep(5)
    page1 = True
    try:
        driver.find_element_by_xpath("//div[@id='root']")
        page1 = True
    except:
        page1 = False

    roads = []
    if page1:
        roads = parse_train_tickets_page_1(driver, departure_town, arrival_town, min_departure_time)
    else:
        roads = parse_train_tickets_page_2(driver, departure_town, arrival_town, min_departure_time)

    return roads


def parse_train_tickets_page_1(driver: webdriver, departure_town: str, arrival_town: str, min_departure_time: datetime):
    max_for_parsing = MAX_COUNT_TICKETS_FOR_PARSING
    print("Всего будем парсить: " + str(max_for_parsing))
    tickets = []
    i = 0
    while i < max_for_parsing:
        for step in range(0, 10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5)
        tickets = driver.find_elements_by_xpath(
            "//div[@class='_151K-8IAD-lVBcM9v84fje']")
        if i == len(tickets):
            max_for_parsing = i
            break
        i = len(tickets)
        print('значение i: ' + str(i))
        print('значение max_for_parsing: ' + str(max_for_parsing))
        print('Бесконечный цикл?')

    print("Билетов всего: " + str(len(tickets)))
    print("Будем парсить: " + str(max_for_parsing))

    roads = []
    for j in range(0, max_for_parsing):
        transport_type = TransportType.TRAIN
        tickets_times = tickets[j].find_elements_by_xpath(".//span[@data-ti='stopover-time']")
        ticket_departure_time = tickets_times[0].text.split(':')
        departure_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                    min_departure_time.year,
                                    min_departure_time.month,
                                    min_departure_time.day,
                                    ticket_departure_time[0],
                                    ticket_departure_time[1],
                                    '00')
        departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

        ticket_arrival_time = tickets_times[1].text.split(':')

        arrival_day = tickets[j].find_elements_by_xpath(".//span[@data-ti='stopover-date']")[1].text.split(' ')[0]
        arrival_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                  min_departure_time.year,
                                  min_departure_time.month,
                                  arrival_day,
                                  ticket_arrival_time[0],
                                  ticket_arrival_time[1],
                                  '00')
        arrival_time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')

        cost = ''
        for i in str(tickets[j].find_element_by_xpath(".//span[@data-ti='price']").text):
            if i.isdigit():
                cost += i
        cost = int(cost)

        link = driver.current_url
        baggage_cost = 0

        print('transport_type: ' + 'PLANE')
        print('departure_town: ' + departure_town)
        print('arrival_town: ' + arrival_town)
        print('departure_time: ' + str(departure_time))
        print('arrival_time: ' + str(arrival_time))
        print('cost: ' + str(cost))
        print('baggage_cost: ' + str(baggage_cost))
        print('link: ' + link)
        road = Road(transport_type=transport_type,
                    departure_town=departure_town,
                    arrival_town=arrival_town,
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    cost=cost,
                    baggage_cost=baggage_cost,
                    link=link
                    )
        roads.append(road)
    driver.quit()
    return roads


def parse_train_tickets_page_2(driver: webdriver, departure_town: str, arrival_town: str, min_departure_time: datetime):
    max_for_parsing = MAX_COUNT_TICKETS_FOR_PARSING
    print("Всего будем парсить: " + str(max_for_parsing))
    tickets = []
    i = 0
    while i < max_for_parsing:
        for step in range(0, 10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5)
        tickets = driver.find_elements_by_xpath(
            "//div[@class='notable__trainCardWrapper__178UB']")
        if i == len(tickets):
            max_for_parsing = i
            break
        i = len(tickets)
        print('значение i: ' + str(i))
        print('значение max_for_parsing: ' + str(max_for_parsing))
        print('Бесконечный цикл?')

    print("Билетов всего: " + str(len(tickets)))
    print("Будем парсить: " + str(max_for_parsing))

    roads = []
    for j in range(0, max_for_parsing):
        transport_type = TransportType.TRAIN
        ticket_departure_time = tickets[j].find_element_by_xpath(".//div[@class='departure_time']").text.split(':')
        departure_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                    min_departure_time.year,
                                    min_departure_time.month,
                                    min_departure_time.day,
                                    ticket_departure_time[0],
                                    ticket_departure_time[1],
                                    '00')
        departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

        ticket_arrival_time = tickets[j].find_element_by_xpath(".//span[@class='schedule_time']").text.split(':')
        day = min_departure_time.day
        # часы приезда < часы выезда => прибыл в следующий день
        if int(ticket_arrival_time[0]) < int(
                ticket_departure_time[0]):  # часы приезда < часы выезда => прибыл в следующий день
            day = min_departure_time.day + 1
        elif int(ticket_arrival_time[0]) == int(ticket_departure_time[0]):  # часы равны
            if int(ticket_arrival_time[1]) < int(ticket_departure_time[1]):  # проверяем минуты
                day = min_departure_time.day + 1
        days_in_way = tickets[j].find_element_by_xpath(".//span[@class='t-txt-s route_time']").text.split(' ')
        if days_in_way[1] == 'д.':
            day += int(days_in_way[0])

        arrival_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                  min_departure_time.year,
                                  min_departure_time.month,
                                  day,
                                  ticket_arrival_time[0],
                                  ticket_arrival_time[1],
                                  '00')
        arrival_time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')


        cost = ''
        cost_block = tickets[j].find_element_by_xpath(".//div[@class='column card_categories']").find_element_by_xpath(".//*").find_elements_by_xpath(".//*")[-1].text
        for i in str(cost_block):
            if i.isdigit():
                cost += i
        cost = int(cost)

        link = tickets[j].find_element_by_xpath(".//a[@class='top_bottom_prices_wrapper top_bottom_prices_wrapper__link']").get_attribute('href')
        baggage_cost = 0

        print('transport_type: ' + 'PLANE')
        print('departure_town: ' + departure_town)
        print('arrival_town: ' + arrival_town)
        print('departure_time: ' + str(departure_time))
        print('arrival_time: ' + str(arrival_time))
        print('cost: ' + str(cost))
        print('baggage_cost: ' + str(baggage_cost))
        print('link: ' + link)
        road = Road(transport_type=transport_type,
                    departure_town=departure_town,
                    arrival_town=arrival_town,
                    departure_time=departure_time,
                    arrival_time=arrival_time,
                    cost=cost,
                    baggage_cost=baggage_cost,
                    link=link
                    )
        roads.append(road)
    # driver.quit()
    return roads


def parse_buses_tickets(departure_town: str, arrival_town: str, min_departure_time: datetime):
    driver = webdriver.Chrome(CHROME_EXE_PATH)
    driver.set_window_size(1500, 1000)
    driver.get("https://bus.tutu.ru/")


class TutuParser(RoadParser, ABC):
    def __init__(self):
        super().__init__()

    def parse_roads(self, transport_types: List[TransportType],
                    departure_town: str, arrival_town: str,
                    min_departure_time: datetime) -> List[Road]:
        roads = []
        for transport in transport_types:
            if transport == TransportType.PLANE:
                roads.extend(parse_avia_tickets(departure_town, arrival_town, min_departure_time))
            elif transport == TransportType.TRAIN:
                roads.extend(parse_train_tickets(departure_town, arrival_town, min_departure_time))
            elif transport == TransportType.BUS:
                roads.extend(parse_buses_tickets(departure_town, arrival_town, min_departure_time))
            else:
                raise NotImplemented()

        return roads

    def can_parse_transport(self, transport_type: TransportType) -> bool:
        if transport_type == TransportType.PLANE:
            return True
        elif transport_type == TransportType.TRAIN:
            return True
        elif transport_type == TransportType.BUS:
            return False
        else:
            raise NotImplemented()