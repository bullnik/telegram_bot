import time
from abc import ABC
from road_parser import *
from road import *
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

# Путь к драйверу хрома чтоб работало, у каждого свой путь... (ауф)
CHROME_EXE_PATH = "C:\\Users\\admin\\Desktop\\chromedriver_win32\\chromedriver.exe"

def get_avia_tickets():
    driver = webdriver.Chrome(executable_path=CHROME_EXE_PATH) #собстна сам драйвер
    driver.get("https://travel.yandex.ru/avia/") # какой сайт запускает
    clear_button = driver.find_element_by_class_name('_1-YdI') # это кнопка чтоб удалить содержимое текстового поля
    print(clear_button) # для проверки что всё норм в консоль пишется элемент
    clear_button.click() # чистим поле чтоб ввести свой город

    #departure = driver.find_element_by_class_name('_3bl6g')
    departure = driver.find_element_by_xpath("//input[@class='_3bl6g input_center']") # это ищется первое поле с городом Откуда
    print(departure) # проверка
    departure.send_keys("Сочи") # тут будет подставляться город Откуда

    # Пока не разобрался как работат ожидания. Надо ждать обновления выпадающего списка
    #departure_dropbox_element = WebDriverWait(driver, 5).until(
    #    EC.visibility_of_any_elements_located((By.CLASS_NAME, '_1mY6J _1QpxA'))
    #)

    # Хреновое название переменной, переделывай. Кароч это из выпадающего списка первый элемент
    time.sleep(1) # костыль, выпадающий список обновляется не моментально
    departure_dropbox_element = driver.find_element_by_xpath("//div[@class='_1mY6J _1QpxA']")
    departure_dropbox_element.click() # там есть выпадающий список. Надо обязательно выбирать город из списка, иначе неизвестный город и иди накуй

    arrival = driver.find_element_by_xpath("//input[@class='_3bl6g input_center']") # Это уже ищется поле с городом Куда (у прошлого элемента класс поменялся, поэтому это пашет)
    print(arrival) # для проверки что всё норм в консоль пишется элемент
    arrival.send_keys("Москва")  # тут будет подставляться город Куда
    time.sleep(1) # опять костыль
    arrival_element = driver.find_element_by_xpath("//div[@class='_1mY6J _1QpxA']") # таже хрень с выпадающим списком
    arrival_element.click()

    print("Откуда: " + departure.get_attribute('value')) # Проверяю что всё правильно подставилось в поля
    print("Куда: " + arrival.get_attribute('value')) #

    # Названия переменных то ещё дерьмо, но надеюсь заставлю себя нормальные придумать
    # тут значит берутся все блоки месяцов (1-31 дни)
    month_periods = driver.find_elements_by_xpath("//div[@class='_1Gwsc']")
    month_name = None
    print(range(0, len(month_periods)))
    for i in range(0, len(month_periods)): # пробегаем по всем блокам месяцов
        month_name = month_periods[i].find_element_by_xpath("//div[@class='_1qrB_ _1bVZZ']")
        print("Проверяется месяц:" + month_name.text)
        if month_name.text == "Октябрь": # ищем блок с нужным месяцем (будет подставляться название месяца)
            print("Месяц правильный. Чотка")
            month_period = month_name.find_element_by_xpath('..') # Сохраняем родителя дива с правильным месяцем
            days_blocks = month_period.find_elements_by_xpath("//div[@class='_3AlmX _38-9Y']") # в блоке одного месяца ищем доступные дни
            day = None
            for i in range(0, len(days_blocks)): # пробегаем по всем доступным дням
                day = days_blocks[i].find_elements_by_xpath(".//*") # получаем всех потомков
                print("Проверяется день:" + day[0].text)
                if day[0].text == '15': # нужен первый блок <span> (будет подставляться день)
                    break
            print("День правильный. Чотка")
            day[0].click() # Нажимаем по дню чтоб выбрать
            break
    # Месяца криво работают почему-то, но день выбирает правильно
    # надо пролистывать список с месяцами чтоб всё вытаскивало
    # и надо кнопку поиска нажимать
    # ну и потом придётся парсить сами билеты

class YandexParser(RoadParser, ABC):
    def __init__(self):
        super().__init__()

    def parse_roads(self, transport_types: List[TransportType],
                    departure_town: str, arrival_town: str,
                    min_departure_time: datetime) -> List[Road]:

        # возвращает список дорог, спаршенных с сайта
        # время отправления: от min_departure_time до конца дня

        raise NotImplemented()

    def can_parse_transport(self, transport_type: TransportType) -> bool:
        if transport_type == TransportType.PLANE:
            return False
        elif transport_type == TransportType.TRAIN:
            return False
        elif transport_type == TransportType.BUS:
            return False
        else:
            raise NotImplemented()
