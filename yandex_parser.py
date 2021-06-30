import datetime
import time
from abc import ABC
from road_parser import *
from road import *
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.touch_actions import TouchActions
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Путь к драйверу хрома чтоб работало, у каждого свой путь... (ауф)
CHROME_EXE_PATH = "C:\\Users\\admin\\Desktop\\chromedriver_win32\\chromedriver.exe"


def get_month_name(month: int) -> str:
    month_names = ['Январь', 'Февраль', 'Март', 'Апрель', 'Май', 'Июнь',
                   'Июль', 'Август', 'Сентябрь', 'Октябрь', 'Ноябрь', 'Декабрь']
    return month_names[month - 1]


def parse_avia_tickets(departure_town: str, arrival_town: str, min_departure_time: datetime):
    driver = webdriver.Chrome(executable_path=CHROME_EXE_PATH)  # собстна сам драйвер
    driver.get("https://travel.yandex.ru/avia/")  # какой сайт запускает
    clear_button = driver.find_element_by_class_name('_1-YdI')  # это кнопка чтоб удалить содержимое текстового поля
    # print(clear_button)  # для проверки что всё норм в консоль пишется элемент
    clear_button.click()  # чистим поле чтоб ввести свой город

    # Ищется первое поле с городом Откуда
    departure = driver.find_element_by_xpath("//input[@class='_3bl6g input_center']")
    print(departure)  # проверка
    departure.send_keys(departure_town)  # тут будет подставляться город Откуда

    # Пока не разобрался как работат ожидания. Надо ждать обновления выпадающего списка
    # departure_dropbox_element = WebDriverWait(driver, 5).until(
    #    EC.visibility_of_any_elements_located((By.CLASS_NAME, '_1mY6J _1QpxA'))
    # )

    # там есть выпадающий список. Надо обязательно выбирать город из списка, иначе неизвестный город и иди накуй
    time.sleep(1)  # костыль, выпадающий список обновляется не моментально
    departure_dropbox_element = driver.find_element_by_xpath("//div[@class='_1mY6J _1QpxA']")
    departure_dropbox_element.click()

    # Ищется поле с городом Куда (у прошлого элемента класс поменялся, поэтому это пашет)
    arrival = driver.find_element_by_xpath("//input[@class='_3bl6g input_center']")
    print(arrival)  # для проверки что всё норм в консоль пишется элемент
    arrival.send_keys(arrival_town)  # тут будет подставляться город Куда
    time.sleep(1)  # опять костыль
    arrival_element = driver.find_element_by_xpath("//div[@class='_1mY6J _1QpxA']")  # таже хрень с выпадающим списком
    arrival_element.click()

    print("Откуда: " + departure.get_attribute('value'))  # Проверяю что всё правильно подставилось в поля
    print("Куда: " + arrival.get_attribute('value'))  #

    scroll_element = driver.find_element_by_xpath("//div[@class='oOXaP']")
    driver.execute_script("arguments[0].scrollTo(0, 3000)", scroll_element)
    # touch = TouchActions(driver)
    # touch.scroll_from_element(scroll_element, 0, 200).perform()

    # тут значит берутся все блоки месяцов (1-31 дни)
    time.sleep(1)
    month_blocks = driver.find_elements_by_xpath("//div[@class='_1Gwsc']")
    print("Блоков с месяцами: " + str(len(month_blocks)))
    # Ищем нужный месяц
    month = []
    all_days = []
    for block in month_blocks:  # пробегаем по всем блокам месяцов
        var_month = block.find_elements_by_xpath(".//*")[0]
        print("Проверяется месяц:" + var_month.text)
        if var_month.text == get_month_name(min_departure_time.month):  # ищем блок с нужным месяцем (будет подставляться название месяца)
            print("Месяц найден. Чотка")
            month.append(var_month)

            # в блоке одного месяца ищем доступные дни
            days_red_blocks = block.find_elements(By.XPATH, ".//div[@class='_3AlmX aUJA2 _38-9Y']")
            days_black_blocks = block.find_elements(By.XPATH, ".//div[@class='_3AlmX _38-9Y']")
            all_days.extend(days_red_blocks + days_black_blocks)
            print("Сколько дней в месяце: " + str(len(all_days)))
    # Находим нужный день
    day = None
    for day_block in all_days:  # пробегаем по всем доступным дням
        day = day_block.find_elements_by_xpath(".//*")  # получаем всех потомков
        print("Проверяется день: " + day[0].text)
        if day[0].text == str(min_departure_time.day):  # нужен первый блок <span> (будет подставляться день)
            print("День правильный. Чотка")
            break
    day[0].click()  # Нажимаем по дню чтоб выбрать
    search_button = driver.find_element_by_xpath("//div[@class='_1XCvB']")
    search_button.click()

    time.sleep(15)
    direct_button = driver.find_element_by_xpath(
        "//button[@class='Button2 YTButton YTButton_theme_secondary YTButton_size_m-inset Button2_width_max Button2_view_default YTButton_kind_check _32KGW']")
    direct_button.click()

    time.sleep(0.5)
    found_tickets_count = int(driver.find_element_by_xpath("//span[@class='rzDEw']").text.split(' ')[1])
    print("Найдено билетов: " + str(found_tickets_count))

    # сколько билетов парсить (берём из админ панели)
    # для тестов пока так сделал
    max = 80

    max_for_parsing = found_tickets_count if found_tickets_count <= max else max
    print("Всего будем парсить: " + str(max_for_parsing))
    tickets = []
    i = 0
    while i < max_for_parsing:
        for step in range(0, 10):
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight)")
            time.sleep(0.5)
        tickets = driver.find_elements_by_xpath("//div[@class='_1y4vO _2-dbu lwCkE _3bJlE dK_Gv']")
        i = len(tickets)
        print('значение i: ' + str(i))
        print('значение max_for_parsing: ' + str(max_for_parsing))
        print('Бесконечный цикл?')

    # Тут сразу из тега <a> можно вытащить href ссылку на покупку билета
    # tickets = driver.find_elements_by_xpath("//a[@class='_25xbA']")
    print("Билетов всего: " + str(len(tickets)))

    roads = []
    for j in range(0, i):
        # ticket = tickets[0]
        transport_type = TransportType.PLANE
        dep_town = departure_town  # Будут подставляться из введённых данных
        arr_town = arrival_town  #
        ticket_departure_time = tickets[j].find_element_by_xpath(".//span[@class='bX2B3 _3c05m JIKEi _2uao0']").text.split(':')
        departure_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                    min_departure_time.year,
                                    min_departure_time.month,
                                    min_departure_time.day,
                                    ticket_departure_time[0],
                                    ticket_departure_time[1],
                                    '00')
        departure_time = datetime.strptime(departure_time, '%Y-%m-%d %H:%M:%S')
        ticket_arrival_time = tickets[j].find_element_by_xpath(".//span[@class='_3c05m JIKEi _2uao0']").text.split(':')
        day = min_departure_time.day
        if int(ticket_arrival_time[0]) < int(ticket_departure_time[0]):
            day = min_departure_time.day + 1
        arrival_time = str.format('{0}-{1}-{2} {3}:{4}:{5}',
                                  min_departure_time.year,
                                  min_departure_time.month,
                                  day,
                                  ticket_arrival_time[0],
                                  ticket_arrival_time[1],
                                  '00')
        arrival_time = datetime.strptime(arrival_time, '%Y-%m-%d %H:%M:%S')
        cost = tickets[j].find_element_by_xpath(".//span[@class='_3XOAe price _1oFrq']").text
        link = tickets[j].find_element_by_xpath(".//a[@class='_25xbA']").get_attribute('href')
        baggage_cost = '0'
        check_box = tickets[j].find_elements_by_xpath(".//input[@class='Checkbox-Control']")[1].get_attribute(
            'aria-checked')
        if check_box == 'false':
            baggage_cost = tickets[j].find_element_by_xpath(".//span[@class='_3XOAe']").text
        print('transport_type: ' + 'PLANE')
        print('departure_town: ' + departure_town)
        print('arrival_town: ' + arrival_town)
        print('departure_time: ' + str(departure_time))
        print('arrival_time: ' + str(arrival_time))
        print('cost: ' + cost)
        print('baggage_cost: ' + baggage_cost)
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
    return roads


class YandexParser(RoadParser, ABC):
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
                raise NotImplemented()
            else:
                raise NotImplemented()

        raise roads

    def can_parse_transport(self, transport_type: TransportType) -> bool:
        if transport_type == TransportType.PLANE:
            return False
        elif transport_type == TransportType.TRAIN:
            return False
        elif transport_type == TransportType.BUS:
            return False
        else:
            raise NotImplemented()
