import datetime
import time
from abc import ABC
from road_parser import *
from road import *
from selenium import webdriver
import selenium.common.exceptions as ex
from selenium.webdriver.common.keys import Keys
import settings

CHROME_EXE_PATH = "chromedriver.exe"
SCROLL_DOWN_STEPS_COUNT = 5
SETTINGS = settings.Settings()


class TutuParser(RoadParser, ABC):
    def __init__(self):
        super().__init__()

    def parse_roads(self, transport_types: List[TransportType],
                    departure_town: str, arrival_town: str,
                    min_departure_time: datetime) -> List[Road]:
        roads = []
        for transport in transport_types:
            if transport == TransportType.PLANE:
                roads.extend(self.parse_avia_tickets(departure_town, arrival_town, min_departure_time))
            elif transport == TransportType.TRAIN:
                roads.extend(self.parse_train_tickets(departure_town, arrival_town, min_departure_time))
            elif transport == TransportType.BUS:
                roads.extend(self.parse_buses_tickets(departure_town, arrival_town, min_departure_time))
            else:
                raise NotImplemented()

        return roads

    def can_parse_transport(self, transport_type: TransportType) -> bool:
        if transport_type == TransportType.PLANE:
            return True
        elif transport_type == TransportType.TRAIN:
            return True
        elif transport_type == TransportType.BUS:
            return True
        else:
            raise NotImplemented()

    def parse_avia_tickets(self, departure_town: str, arrival_town: str, min_departure_time: datetime) -> List[Road]:
        driver = webdriver.Chrome(CHROME_EXE_PATH)
        driver.set_window_size(1500, 1000)
        driver.get("https://avia.tutu.ru/")

        time.sleep(1)
        try:
            departure = driver.find_element_by_xpath("//input[@class='o33560 o33576']")
        except ex.NoSuchElementException:
            print('Не удалось найти поле ввода Откуда')
            return []
        print(departure)  # проверка
        departure.send_keys(departure_town)

        time.sleep(1)
        try:
            arrival = driver.find_element_by_xpath("//input[@class='o33560 o33641']")
        except ex.NoSuchElementException:
            print('Не удалось найти поле ввода Куда')
            return []
        print(arrival)  # для проверки что всё норм в консоль пишется элемент
        arrival.send_keys(arrival_town)  # тут будет подставляться город Куда

        time.sleep(1)
        print("Откуда: " + departure.get_attribute('value'))  # Проверяю что всё правильно подставилось в поля
        print("Куда: " + arrival.get_attribute('value'))  #

        try:
            date_block = driver.find_element_by_xpath("//input[@class='o33560 o33663 o33658 o33659']")
        except ex.NoSuchElementException:
            print('Не удалось найти поле ввода даты')
            return []
        print(date_block)
        date_block.send_keys(min_departure_time.strftime('%d.%m.%Y'))
        time.sleep(1)

        try:
            search_button = driver.find_element_by_xpath("//button[@class='order-group-element o33688 o33693 o33695']")
        except ex.NoSuchElementException:
            print("Не удалось найти кнопку поиска")
            return []
        search_button.click()

        time.sleep(1)
        max_for_parsing = SETTINGS.get_max_count_parsed_roads()
        print("Всего будем парсить: " + str(max_for_parsing))
        tickets = []
        i = 0
        while i < max_for_parsing:
            for step in range(0, SCROLL_DOWN_STEPS_COUNT):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
            try:
                tickets = driver.find_elements_by_xpath("//div[@class='_3myc0zS07d6p2suflgjuDQ']")
            except ex.NoSuchElementException:
                print("Не удалось найти билеты")
                return []
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
            try:
                route_type = tickets[j].find_element_by_xpath(".//span[@data-ti='route_main_line']")
            except ex.NoSuchElementException:
                print("Не удалось получить тип билета")
                continue
            if route_type.text != 'Прямой':
                continue
            transport_type = TransportType.PLANE
            try:
                tickets_times = tickets[j].find_elements_by_xpath(".//span[@class='o33733']")
            except ex.NoSuchElementException:
                print("Не удалось получить время")
                continue
            if len(tickets_times) < 2:
                print("Не удалось распарсить время")
                continue
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
            arrival_day = min_departure_time.day
            # часы приезда < часы выезда => прибыл в следующий день
            if int(ticket_arrival_time[0]) <= int(ticket_departure_time[0]):
                arrival_day = min_departure_time.day + 1
            arrival_month = min_departure_time.month
            if arrival_day < departure_time.day:
                arrival_month = min_departure_time.month + 1
            arrival_year = min_departure_time.year
            if arrival_month < departure_time.month:
                arrival_year = min_departure_time.year + 1
            arrival_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                      arrival_year,
                                      arrival_month,
                                      arrival_day,
                                      ticket_arrival_time[0],
                                      ticket_arrival_time[1],
                                      '00')
            arrival_time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')

            cost = ''
            try:
                cost_block = tickets[j].find_element_by_xpath(".//span[@data-ti='price']")
            except ex.NoSuchElementException:
                print("Не удалось получить цену билета")
                continue
            for i in str(cost_block.text):
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

    def parse_train_tickets(self, departure_town: str, arrival_town: str, min_departure_time: datetime) -> List[Road]:
        driver = webdriver.Chrome(CHROME_EXE_PATH)
        driver.set_window_size(1500, 1000)
        driver.get("https://www.tutu.ru/poezda/")

        time.sleep(1)
        try:
            departure = driver.find_element_by_xpath(
                "//input[@class='input_field j-station_input  j-station_input_from']")
        except ex.NoSuchElementException:
            print('Не удалось найти поле ввода Откуда')
            return []
        print(departure)  # проверка
        departure.send_keys(departure_town)

        time.sleep(1)
        try:
            arrival = driver.find_element_by_xpath("//input[@class='input_field j-station_input  j-station_input_to']")
        except ex.NoSuchElementException:
            print('Не удалось найти поле ввода Куда')
            return []
        print(arrival)  # для проверки что всё норм в консоль пишется элемент
        arrival.send_keys(arrival_town)  # тут будет подставляться город Куда

        time.sleep(1)
        print("Откуда: " + departure.get_attribute('value'))  # Проверяю что всё правильно подставилось в поля
        print("Куда: " + arrival.get_attribute('value'))  #

        try:
            date_block = driver.find_element_by_xpath(
                "//input[@class='input_field j-permanent_open j-input j-date_to']")
        except ex.NoSuchElementException:
            print('Не удалось найти поле ввода даты')
            return []
        print(date_block)
        date_block.send_keys(min_departure_time.strftime('%d.%m.%Y'))
        time.sleep(1)

        try:
            search_button = driver.find_element_by_xpath(
                "//button[@class='b-button__arrow__button j-button j-button-submit _title j-submit_button _blue']")
        except ex.NoSuchElementException:
            print("Не удалось найти кнопку поиска")
            return []
        search_button.click()

        time.sleep(5)

        try:
            driver.find_element_by_xpath("//div[@id='root']")
            page1 = True
        except ex.NoSuchElementException:
            page1 = False

        if page1:
            roads = self.parse_train_tickets_page_1(driver, departure_town, arrival_town, min_departure_time)
        else:
            roads = self.parse_train_tickets_page_2(driver, departure_town, arrival_town, min_departure_time)

        return roads

    @staticmethod
    def parse_train_tickets_page_1(driver: webdriver, departure_town: str, arrival_town: str,
                                   min_departure_time: datetime) -> List[Road]:
        max_for_parsing = SETTINGS.get_max_count_parsed_roads()
        print("Всего будем парсить: " + str(max_for_parsing))
        tickets = []
        i = 0
        while i < max_for_parsing:
            for step in range(0, SCROLL_DOWN_STEPS_COUNT):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
            try:
                tickets = driver.find_elements_by_xpath(
                    "//div[@class='_151K-8IAD-lVBcM9v84fje']")
            except ex.NoSuchElementException:
                print("Не удалось получить билеты")
                return []
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
            try:
                tickets_times = tickets[j].find_elements_by_xpath(".//span[@data-ti='stopover-time']")
            except ex.NoSuchElementException:
                print("Не удалось получить время")
                continue
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

            try:
                arrival_day = int(tickets[j].find_elements_by_xpath(
                    ".//span[@data-ti='stopover-date']")[1].text.split(' ')[0])
            except ex.NoSuchElementException:
                print("Не удалось получить день приезда")
                continue
            arrival_month = min_departure_time.month
            if arrival_day < departure_time.day:
                arrival_month = min_departure_time.month + 1
            arrival_year = min_departure_time.year
            if arrival_month < departure_time.month:
                arrival_year = min_departure_time.year + 1
            arrival_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                      arrival_year,
                                      arrival_month,
                                      arrival_day,
                                      ticket_arrival_time[0],
                                      ticket_arrival_time[1],
                                      '00')
            arrival_time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')

            cost = ''
            try:
                cost_block = tickets[j].find_element_by_xpath(".//span[@data-ti='price']")
            except ex.NoSuchElementException:
                print("Не удалось получить цену билета")
                continue
            for i in str(cost_block.text):
                if i.isdigit():
                    cost += i
            cost = int(cost)

            link = driver.current_url
            baggage_cost = 0

            print('transport_type: ' + 'TRAIN')
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

    @staticmethod
    def parse_train_tickets_page_2(driver: webdriver, departure_town: str, arrival_town: str,
                                   min_departure_time: datetime) -> List[Road]:
        max_for_parsing = SETTINGS.get_max_count_parsed_roads()
        print("Всего будем парсить: " + str(max_for_parsing))
        tickets = []
        i = 0
        while i < max_for_parsing:
            for step in range(0, SCROLL_DOWN_STEPS_COUNT):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
            try:
                tickets = driver.find_elements_by_xpath(
                    "//div[@class='notable__trainCardWrapper__178UB']")
            except ex.NoSuchElementException:
                print("Не удалось найти билеты")
                return []
            if i == len(tickets):
                max_for_parsing = i
                break
            i = len(tickets)
            print('значение i: ' + str(i))
            print('значение max_for_parsing: ' + str(max_for_parsing))
            print('Бесконечный цикл?')

        print("Будем парсить: " + str(max_for_parsing))

        roads = []
        for j in range(0, max_for_parsing):
            transport_type = TransportType.TRAIN
            try:
                ticket_departure_time = tickets[j].find_element_by_xpath(
                    ".//div[@class='departure_time']").text.split(':')
            except ex.NoSuchElementException:
                print("Не удалось получить время выезда")
                continue
            departure_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                        min_departure_time.year,
                                        min_departure_time.month,
                                        min_departure_time.day,
                                        ticket_departure_time[0],
                                        ticket_departure_time[1],
                                        '00')
            departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

            try:
                ticket_arrival_time = tickets[j].find_element_by_xpath(
                    ".//span[@class='schedule_time']").text.split(':')
            except ex.NoSuchElementException:
                print("Не удалось получить время приезда")
                continue
            arrival_day = min_departure_time.day
            # часы приезда < часы выезда => прибыл в следующий день
            if int(ticket_arrival_time[0]) < int(
                    ticket_departure_time[0]):  # часы приезда < часы выезда => прибыл в следующий день
                arrival_day = min_departure_time.day + 1
            elif int(ticket_arrival_time[0]) == int(ticket_departure_time[0]):  # часы равны
                if int(ticket_arrival_time[1]) < int(ticket_departure_time[1]):  # проверяем минуты
                    arrival_day = min_departure_time.day + 1
            try:
                days_in_way = tickets[j].find_element_by_xpath(
                    ".//span[@class='t-txt-s route_time']").text.split(' ')
            except ex.NoSuchElementException:
                print("Не удалось получить количество дней в пути")
                continue
            if days_in_way[1] == 'д.':
                arrival_day += int(days_in_way[0])
            arrival_month = min_departure_time.month
            if arrival_day < departure_time.day:
                arrival_month = min_departure_time.month + 1
            arrival_year = min_departure_time.year
            if arrival_month < departure_time.month:
                arrival_year = min_departure_time.year + 1
            arrival_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                      arrival_year,
                                      arrival_month,
                                      arrival_day,
                                      ticket_arrival_time[0],
                                      ticket_arrival_time[1],
                                      '00')
            arrival_time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')

            cost = ''
            try:
                cost_block = tickets[j].find_element_by_xpath(
                    ".//div[@class='column card_categories']").find_element_by_xpath(
                    ".//*").find_elements_by_xpath(".//*")[-1]
            except ex.NoSuchElementException:
                print("Не удалось получить цену билета")
                continue
            for i in str(cost_block.text):
                if i.isdigit():
                    cost += i
            cost = int(cost)

            try:
                link = tickets[j].find_element_by_xpath(
                    ".//a[@class='top_bottom_prices_wrapper top_bottom_prices_wrapper__link']").get_attribute('href')
            except ex.NoSuchElementException:
                print("Не удалось получить ссылку")
                link = driver.current_url
            baggage_cost = 0

            print('transport_type: ' + 'TRAIN')
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

    def parse_buses_tickets(self, departure_town: str, arrival_town: str, min_departure_time: datetime) -> List[Road]:
        driver = webdriver.Chrome(CHROME_EXE_PATH)
        driver.set_window_size(1500, 1000)
        driver.get("https://bus.tutu.ru/")

        time.sleep(1)
        try:
            departure = driver.find_element_by_xpath("//input[@placeholder='Откуда']")
        except ex.NoSuchElementException:
            print('Не удалось найти поле ввода Откуда')
            return []
        print(departure)  # проверка
        departure.send_keys(departure_town)

        time.sleep(1)
        try:
            arrival = driver.find_element_by_xpath("//input[@placeholder='Куда']")
        except ex.NoSuchElementException:
            print('Не удалось найти поле ввода Куда')
            return []
        print(arrival)  # для проверки что всё норм в консоль пишется элемент
        arrival.send_keys(arrival_town)  # тут будет подставляться город Куда

        time.sleep(1)
        print("Откуда: " + departure.get_attribute('value'))  # Проверяю что всё правильно подставилось в поля
        print("Куда: " + arrival.get_attribute('value'))  #

        try:
            date_block = driver.find_element_by_xpath("//input[@placeholder='Дата']")
        except ex.NoSuchElementException:
            print("Не удалось найти поле ввода даты")
            return []
        print(date_block)
        for i in range(0, 15):
            date_block.send_keys(Keys.BACKSPACE)
        date_block.send_keys(min_departure_time.strftime('%d.%m.%Y'))
        time.sleep(1)

        try:
            search_button = driver.find_element_by_xpath("//button[@class='order-group-element o3338 o3343 o3345']")
        except ex.NoSuchElementException:
            print("Не удалось найти кнопку поиска")
            return []
        search_button.click()

        # Если не перешло на новую страницу - то выходим
        current_url = driver.current_url
        wait_time = 0
        while driver.current_url == current_url:
            if wait_time == 10:
                return []
            time.sleep(1)
            wait_time += 1

        time.sleep(10)
        try:
            div_element = driver.find_element_by_xpath("//div[@class='index__wrapper___gzfy3']")
        except ex.NoSuchElementException:
            print("Не удалось получить билеты")
            return []

        try:
            div_element.find_element_by_xpath(".//tbody[@itemprop='offers']")
            page1 = True
        except ex.NoSuchElementException:
            page1 = False

        if page1:
            roads = self.parse_buses_tickets_page_1(driver, departure_town, arrival_town, min_departure_time)
        else:
            roads = self.parse_buses_tickets_page_2(driver, departure_town, arrival_town, min_departure_time)

        return roads

    @staticmethod
    def parse_buses_tickets_page_1(driver: webdriver, departure_town: str, arrival_town: str,
                                   min_departure_time: datetime) -> List[Road]:
        max_for_parsing = SETTINGS.get_max_count_parsed_roads()
        print("Всего будем парсить: " + str(max_for_parsing))
        tickets = []
        i = 0
        while i < max_for_parsing:
            for step in range(0, SCROLL_DOWN_STEPS_COUNT):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
            try:
                tickets = driver.find_elements_by_xpath(
                    "//tr[@class='index__row___3rPq4 index__opened_row_desktop___ZZ3_E']")
            except ex.NoSuchElementException:
                print("Не удалось найти билеты")
                return []
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
            transport_type = TransportType.BUS
            try:
                ticket_departure_time = tickets[j].find_element_by_xpath(
                    ".//td[@class='index__departure___16vG_']").text.split(':')
            except ex.NoSuchElementException:
                print("Не удалось найти время выезда")
                continue
            departure_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                        min_departure_time.year,
                                        min_departure_time.month,
                                        min_departure_time.day,
                                        ticket_departure_time[0],
                                        ticket_departure_time[1],
                                        '00')
            departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

            try:
                ticket_arrival_time = tickets[j].find_element_by_xpath(
                    ".//td[@class='index__arrival___33ybQ']").text.split(':')
            except ex.NoSuchElementException:
                print("Не удалось найти время приезда")
                continue
            arrival_day = min_departure_time.day
            if int(ticket_arrival_time[0]) <= int(ticket_departure_time[0]):
                arrival_day = min_departure_time.day + 1
            arrival_month = min_departure_time.month
            if arrival_day < departure_time.day:
                arrival_month = min_departure_time.month + 1
            arrival_year = min_departure_time.year
            if arrival_month < departure_time.month:
                arrival_year = min_departure_time.year + 1
            arrival_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                      arrival_year,
                                      arrival_month,
                                      arrival_day,
                                      ticket_arrival_time[0],
                                      ticket_arrival_time[1],
                                      '00')
            arrival_time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')

            cost = ''
            try:
                cost_block = tickets[j].find_element_by_xpath(
                    ".//td[@class='index__buy___2rAq9 index__not_for_sale___3RyM0 index__no_offers_for_sale___1FI53']")
            except ex.NoSuchElementException:
                print("Не удалось получить цену")
                continue
            for i in str(cost_block.text):
                if i.isdigit():
                    cost += i
            cost = int(cost)

            link = driver.current_url
            baggage_cost = 0

            print('transport_type: ' + 'BUS')
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

    @staticmethod
    def parse_buses_tickets_page_2(driver: webdriver, departure_town: str, arrival_town: str,
                                   min_departure_time: datetime) -> List[Road]:
        max_for_parsing = SETTINGS.get_max_count_parsed_roads()
        print("Всего будем парсить: " + str(max_for_parsing))
        tickets = []
        i = 1
        try:
            tickets += driver.find_elements_by_xpath(
                "//div[@class='index__offer___1pMh_ index__hover___2AZR1 index__cheapest___29juA']")
        except ex.NoSuchElementException:
            print("Не удалось получить самый дешёвый билет")
        while i < max_for_parsing:
            for step in range(0, SCROLL_DOWN_STEPS_COUNT):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
            try:
                tickets += driver.find_elements_by_xpath("//div[@class='index__offer___1pMh_']")
            except ex.NoSuchElementException:
                print("Не удалось получить билеты")
                return []
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
            transport_type = TransportType.BUS
            try:
                ticket_departure_time = tickets[j].find_element_by_xpath(
                    ".//span[@class='index__departure_time___j_JX4']").text.split(':')
            except ex.NoSuchElementException:
                print("Не удалось получить время выезда")
                continue
            departure_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                        min_departure_time.year,
                                        min_departure_time.month,
                                        min_departure_time.day,
                                        ticket_departure_time[0],
                                        ticket_departure_time[1],
                                        '00')
            departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')
            try:
                ticket_arrival_time = tickets[j].find_element_by_xpath(
                    ".//span[@class='index__arrival_time___161Ry']").text.split(':')
            except ex.NoSuchElementException:
                print("Не удалось получить время приезда")
                continue
            arrival_day = min_departure_time.day
            if int(ticket_arrival_time[0]) <= int(ticket_departure_time[0]):
                arrival_day = min_departure_time.day + 1
            arrival_month = min_departure_time.month
            if arrival_day < departure_time.day:
                arrival_month = min_departure_time.month + 1
            arrival_year = min_departure_time.year
            if arrival_month < departure_time.month:
                arrival_year = min_departure_time.year + 1
            arrival_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                      arrival_year,
                                      arrival_month,
                                      arrival_day,
                                      ticket_arrival_time[0],
                                      ticket_arrival_time[1],
                                      '00')
            arrival_time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')

            cost = ''
            try:
                cost_block = tickets[j].find_element_by_xpath(".//div[@class='index__default_price___2in_N']")
            except ex.NoSuchElementException:
                print("Не удалось получить цену билета")
                continue
            for i in str(cost_block.text):
                if i.isdigit():
                    cost += i
            cost = int(cost)

            link = driver.current_url
            baggage_cost = 0

            print('transport_type: ' + 'BUS')
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
