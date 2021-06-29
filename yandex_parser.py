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
    departure_dropbox_element = driver.find_element_by_xpath("//div[@class='_1mY6J _1QpxA']")
    time.sleep(1) # костыль, выпадающий список обновляется не моментально
    departure_dropbox_element.click() # там есть выпадающий список. Надо обязательно выбирать город из списка, иначе неизвестный город и иди накуй

    arrival = driver.find_element_by_xpath("//input[@class='_3bl6g input_center']") # Это уже ищется поле с городом Куда (у прошлого элемента класс поменялся, поэтому это пашет)
    print(arrival) # для проверки что всё норм в консоль пишется элемент
    arrival.send_keys("Москва")  # тут будет подставляться город Куда
    time.sleep(1) # опять костыль
    arrival_element = driver.find_element_by_xpath("//div[@class='_1mY6J _1QpxA']") # таже хрень с выпадающим списком
    arrival_element.click()

    print(departure.get_attribute('value')) # Проверяю что всё правильно подставилось в поля
    print(arrival.get_attribute('value')) #

    # Дальше тут надо ещё выбор даты прикручивать сюка((((


class YandexParser(RoadParser, ABC):
    def parse_roads(self, transport_types: List[TransportType],
                    departure_town: str, arrival_town: str) -> List[Road]:
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
