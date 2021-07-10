import datetime
import time
from abc import ABC
from road_parser import *
from road import *
from selenium import webdriver
import selenium.common.exceptions as ex
from selenium.webdriver.common.by import By
import settings

CHROME_EXE_PATH = "chromedriver.exe"
SEARCH_ERROR_TIME_WAIT = 5
SEARCH_DIRECT_TICKETS = False
SCROLL_DOWN_STEPS_COUNT = 5
SETTINGS = settings.Settings()


def get_month_name(month: int) -> str:
    month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                   'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    return month_names[month - 1]


class YandexParser(RoadParser, ABC):
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

    @staticmethod
    def data_entry_for_search(driver: webdriver,
                              departure_town: str, arrival_town: str,
                              min_departure_time: datetime, transport_type: str) -> bool:
        driver.set_window_size(1500, 1000)
        driver.get(str.format("https://travel.yandex.ru/{0}/", transport_type))  # какой сайт запускает

        time.sleep(1)
        try:
            clear_button = driver.find_element_by_class_name('_1-YdI')  # это кнопка чтоб удалить содержимое текстового поля
        except ex.NoSuchElementException:
            print("Не удалось найти кнопку очистки поля Откуда")
            return False
        clear_button.click()  # чистим поле чтоб ввести свой город

        # Ищется первое поле с городом Откуда
        time.sleep(1)
        try:
            departure = driver.find_element_by_xpath("//input[@class='_3bl6g input_center']")
        except ex.NoSuchElementException:
            print('Не удалось найти поле ввода Откуда')
            return False
        print(departure)  # проверка
        departure.send_keys(departure_town)  # тут будет подставляться город Откуда

        # там есть выпадающий список. Надо обязательно выбирать город из списка, иначе неизвестный город и иди накуй
        departure_dropbox_element = None
        is_dropbox_update = False
        try_count = 0
        while not is_dropbox_update:
            if try_count == SEARCH_ERROR_TIME_WAIT:
                print("Неверное название города Откуда")
                driver.quit()
                return False
            try:
                time.sleep(1)  # костыль, выпадающий список обновляется не моментально
                departure_dropbox_element = driver.find_element_by_xpath("//div[@class='_1mY6J _1QpxA']")
                dropbox_element_text = departure_dropbox_element.find_elements_by_xpath(".//*")[0].text
                if dropbox_element_text.find(departure_town) != -1:
                    is_dropbox_update = True
            except ex.NoSuchElementException:
                print("Нехватило времени")
                try_count += 1
        departure_dropbox_element.click()

        # Ищется поле с городом Куда (у прошлого элемента класс поменялся, поэтому это пашет)
        time.sleep(1)
        try:
            arrival = driver.find_element_by_xpath("//input[@class='_3bl6g input_center']")
        except ex.NoSuchElementException:
            print('Не удалось найти поле ввода Куда')
            return False
        print(arrival)  # для проверки что всё норм в консоль пишется элемент
        arrival.send_keys(arrival_town)  # тут будет подставляться город Куда

        arrival_dropbox_element = None
        is_dropbox_update = False
        try_count = 0
        while not is_dropbox_update:
            if try_count == SEARCH_ERROR_TIME_WAIT:
                print("Прямых маршрутов не существует или неверное название города Куда")
                driver.quit()
                return False
            try:
                time.sleep(1)  # опять костыль
                arrival_dropbox_element = driver.find_element_by_xpath("//div[@class='_1mY6J _1QpxA']")
                dropbox_element_text = arrival_dropbox_element.find_elements_by_xpath(".//*")[0].text
                if dropbox_element_text.find(arrival_town) != -1:
                    is_dropbox_update = True
            except ex.NoSuchElementException:
                print("Нехватило времени")
                try_count += 1
        arrival_dropbox_element.click()

        print("Откуда: " + departure.get_attribute('value'))  # Проверяю что всё правильно подставилось в поля
        print("Куда: " + arrival.get_attribute('value'))  #

        try:
            scroll_element = driver.find_element_by_xpath("//div[@class='oOXaP']")
        except ex.NoSuchElementException:
            print("Не удалось найти колендарь выбора дня")
            return False
        driver.execute_script("arguments[0].scrollTo(0, 3000)", scroll_element)

        # тут значит берутся все блоки месяцов (1-31 дни)
        time.sleep(1)
        try:
            month_blocks = driver.find_elements_by_xpath("//div[@class='_1Gwsc']")
        except ex.NoSuchElementException:
            print("Не удалось найти блоки с месяцами")
            return False
        print("Блоков с месяцами: " + str(len(month_blocks)))
        # Ищем нужный месяц
        month = []
        all_days = []
        for block in month_blocks:  # пробегаем по всем блокам месяцов
            var_month = block.find_elements_by_xpath(".//*")[0]
            print("Проверяется месяц:" + var_month.text)
            if var_month.text == get_month_name(
                    min_departure_time.month):  # ищем блок с нужным месяцем (будет подставляться название месяца)
                print("Месяц найден. Чотка")
                month.append(var_month)

                # в блоке одного месяца ищем доступные дни
                try:
                    days_red_blocks = block.find_elements(By.XPATH, ".//div[@class='_3AlmX aUJA2 _38-9Y']")
                    days_black_blocks = block.find_elements(By.XPATH, ".//div[@class='_3AlmX _38-9Y']")
                except ex.NoSuchElementException:
                    print("Не удалось найти дни в блоке месяца")
                    return False
                all_days.extend(days_red_blocks + days_black_blocks)
                print("Сколько дней в месяце: " + str(len(all_days)))
        # Находим нужный день
        day = None
        for day_block in all_days:  # пробегаем по всем доступным дням
            day = day_block.find_elements_by_xpath(".//*")  # получаем всех потомков
            print("Проверяется день: " + day[0].text)
            if day[0].text == str(min_departure_time.day):  # нужен первый блок <span> (будет подставляться день)
                print("День правильный")
                break
        day[0].click()  # Нажимаем по дню чтоб выбрать
        try:
            search_button = driver.find_element_by_xpath("//div[@class='_1XCvB']")
        except ex.NoSuchElementException:
            print("Не удалось найти кнопку поиска")
            return False
        search_button.click()

        time.sleep(2)
        try:
            driver.find_element_by_xpath("//h1[@class='_12F9-']")
            return False
        except ex.NoSuchElementException:
            return True

    def parse_avia_tickets(self, departure_town: str, arrival_town: str, min_departure_time: datetime) -> List[Road]:
        driver = webdriver.Chrome(executable_path=CHROME_EXE_PATH)  # собстна сам драйвер
        search_result = self.data_entry_for_search(driver=driver,
                                                   departure_town=departure_town,
                                                   arrival_town=arrival_town,
                                                   min_departure_time=min_departure_time,
                                                   transport_type='avia')
        if not search_result:
            driver.quit()
            return []

        # time.sleep(3)
        time.sleep(10)

        # Кнопка "Без пересадок"
        if SEARCH_DIRECT_TICKETS:
            direct_button = driver.find_element_by_xpath(
                "//button[@class='Button2 YTButton YTButton_theme_secondary YTButton_size_m-inset Button2_width_max "
                "Button2_view_default YTButton_kind_check _32KGW']")
            try:
                direct_button.click()
            except ex.ElementClickInterceptedException:
                print('Билетов без пересадок нет')
                driver.quit()
                return []
            time.sleep(0.5)

        max_for_parsing = SETTINGS.get_max_count_parsed_roads()
        print("Всего будем парсить: " + str(max_for_parsing))
        tickets = []
        i = 0
        while i < max_for_parsing:
            for step in range(0, SCROLL_DOWN_STEPS_COUNT):
                driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
                time.sleep(0.5)
            try:
                tickets = driver.find_elements_by_xpath("//div[@class='_1y4vO _2-dbu lwCkE _3bJlE dK_Gv']")
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

        roads = []
        for j in range(0, max_for_parsing):
            transport_type = TransportType.PLANE
            try:
                ticket_departure_time = tickets[j].find_element_by_xpath(
                    ".//span[@class='bX2B3 _3c05m JIKEi _2uao0']").text.split(':')
            except:
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
                    ".//span[@class='_3c05m JIKEi _2uao0']").text.split(':')
            except ex.NoSuchElementException:
                print("Не удалось получить время приезда")
                continue
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
            try:
                cost_block = tickets[j].find_element_by_xpath(".//span[@class='_3XOAe price _1oFrq']")
            except ex.NoSuchElementException:
                print("Не удалось получить цену билета")
                continue
            cost = ''
            for i in str(cost_block.text):
                if i.isdigit():
                    cost += i
            cost = int(cost)
            try:
                link = tickets[j].find_element_by_xpath(".//a[@class='_25xbA']").get_attribute('href')
            except ex.NoSuchElementException:
                print("Не удалось получить сслку на билет")
                link = driver.current_url

            baggage_cost = 0
            try:
                check_box = tickets[j].find_elements_by_xpath(".//input[@class='Checkbox-Control']")[1].get_attribute(
                    'aria-checked')
            except ex.NoSuchElementException:
                print("Не удалось получить статус багажа")
                check_box = 'true'
            if check_box == 'false':
                baggage_cost = ''
                try:
                    baggage_cost_box = tickets[j].find_element_by_xpath(".//span[@class='_3XOAe']")
                    for i in str(baggage_cost_box.text):
                        if i.isdigit():
                            baggage_cost += i
                    baggage_cost = int(baggage_cost)
                except ex.NoSuchElementException:
                    print("Не удалось получить цену багажа")
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
        driver = webdriver.Chrome(executable_path=CHROME_EXE_PATH)  # собстна сам драйвер
        search_result = self.data_entry_for_search(driver=driver,
                                                   departure_town=departure_town,
                                                   arrival_town=arrival_town,
                                                   min_departure_time=min_departure_time,
                                                   transport_type='trains')
        if not search_result:
            driver.quit()
            return []

        time.sleep(3)

        # сколько билетов парсить (берём из админ панели)
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
                    "//div[@class='_1y4vO _2-dbu lwCkE _34jm4 _1DCdL L84HM _1I3zI _3yorf']")
                # _1y4vO _2-dbu lwCkE _34jm4 _1DCdL L84HM _1I3zI STrwo root_desktop
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

        roads = []
        for j in range(0, max_for_parsing):
            cost = ''
            try:
                ticket_block_cost = tickets[j].find_element_by_xpath(
                    ".//div[@class='_26a8m _2Odvx _1KHmH']").find_elements_by_xpath(".//*")[0]
                # _26a8m _2diRi _1KHmH
            except ex.NoSuchElementException:
                print("Не удалось получить цену билета")
                continue
            except IndexError:
                continue
            if ticket_block_cost.text == 'Билеты в кассах' or ticket_block_cost.text == 'Места закончились':
                continue
            for i in ticket_block_cost.text:
                if i.isdigit():
                    cost += i
            try:
                cost = int(cost)
            except ValueError:
                print("Не удалось получить цену билета")
                continue

            transport_type = TransportType.TRAIN
            try:
                tickets_time = tickets[j].find_element_by_xpath(".//div[@class='points _166IL _2GPch kHxiA']") \
                    .find_elements_by_xpath(".//span[@class='time']")
            except ex.NoSuchElementException:
                print("Не удалось получить время")
                continue
            ticket_departure_time = tickets_time[0].text.split(':')
            departure_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                        min_departure_time.year,
                                        min_departure_time.month,
                                        min_departure_time.day,
                                        ticket_departure_time[0],
                                        ticket_departure_time[1],
                                        '00')
            departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')

            ticket_arrival_time = tickets_time[1].text.split(':')
            arrival_day = min_departure_time.day
            if int(ticket_arrival_time[0]) < int(
                    ticket_departure_time[0]):  # часы приезда < часы выезда => прибыл в следующий день
                arrival_day = min_departure_time.day + 1
            elif int(ticket_arrival_time[0]) == int(ticket_departure_time[0]):  # часы равны
                if int(ticket_arrival_time[1]) < int(ticket_departure_time[1]):  # проверяем минуты
                    arrival_day = min_departure_time.day + 1
            # если часы и минуты равны => сдедующий блок проверки
            # парсим время в пути
            # если есть дни => прибавляем количество дней
            try:
                days_in_way = tickets[j].find_element_by_xpath(".//div[@class='_3BdRQ _1dbOp _2uao0']").text.split(' ')
            except ex.NoSuchElementException:
                print("Не удалось получить количество дней в пути")
                continue
            if days_in_way[1] == 'дн.':
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
            try:
                link = tickets[j].find_element_by_xpath(
                    ".//a[@class='Button2 YTButton YTButton_theme_primary YTButton_size_m-inset Button2_width_max "
                    "Button2_view_default Button2_type_link']").get_attribute('href')
                # "Button2 YTButton YTButton_theme_primary YTButton_size_m-inset Button2_width_max "
                # "Button2_view_default Button2_type_router-link"
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
        driver = webdriver.Chrome(executable_path=CHROME_EXE_PATH)  # собстна сам драйвер
        search_result = self.data_entry_for_search(driver=driver,
                                                   departure_town=departure_town,
                                                   arrival_town=arrival_town,
                                                   min_departure_time=min_departure_time,
                                                   transport_type='buses')
        if not search_result:
            driver.quit()
            return []

        #time.sleep(3)
        time.sleep(10)

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
                    "//div[@class='_1y4vO _2-dbu lwCkE _34jm4 _1DCdL L84HM _1I3zI _3wScJ udQ3v']")
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

        roads = []
        for j in range(0, max_for_parsing):
            transport_type = TransportType.BUS
            try:
                tickets_time = tickets[j].find_elements_by_xpath(".//span[@class='_3c05m JIKEi _2uao0']")
            except ex.NoSuchElementException:
                print("Не удалось получить время")
                continue
            ticket_departure_time = tickets_time[0].text.split(':')
            departure_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                        min_departure_time.year,
                                        min_departure_time.month,
                                        min_departure_time.day,
                                        ticket_departure_time[0],
                                        ticket_departure_time[1],
                                        '00')
            departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')
            ticket_arrival_time = tickets_time[1].text.split(':')

            arrival_day = min_departure_time.day
            if int(ticket_arrival_time[0]) < int(
                    ticket_departure_time[0]):  # часы приезда < часы выезда => прибыл в следующий день
                arrival_day = min_departure_time.day + 1
            elif int(ticket_arrival_time[0]) == int(ticket_departure_time[0]):  # часы равны
                if int(ticket_arrival_time[1]) < int(ticket_departure_time[1]):  # проверяем минуты
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
                cost_block = tickets[j].find_element_by_xpath(".//span[@class='_3XOAe _2q0ht']")
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
            print('link: ' + 'Страница со всеми билетами:' + link)
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
