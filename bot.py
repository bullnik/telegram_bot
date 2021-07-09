import asyncio
import time
from threading import Thread
from typing import List
import telebot
from telebot import types
from Progress import Progress
from controller import Controller
from answer import AnswerToUserRouteRequest
from request import UserRequest
from road import TransportType
from unfinished_request import UnfinishedRequest

token = "801332145:AAGpj1_4Pm4WtjdDi8QsRxdb0F3GaShGr_M"  # @chimberbembra_bot
bot = telebot.TeleBot(token)
start_message = "Используйте следующие команды:\n" \
                "/help - помощь\n" \
                "/favorites - избранное\n" \
                "/route - построить маршрут\n" \
                "/history - история моих запросов"
controller = Controller()


@bot.message_handler(commands=['start', 'help'])
def command_help(message):
    bot.reply_to(message, start_message)


@bot.message_handler(commands=['history'])
def command_history(message):
    requests = controller.get_history(message.from_user.id, 10)
    history = requests_to_string(requests)
    if len(history) == 0:
        bot.reply_to(message, text='Записи не найдены')
    else:
        history += '/load_last [Номер записи] - загрузить маршрут из истории'
        bot.reply_to(message, text=history)


@bot.message_handler(commands=['favorites'])
def command_favourites(message):
    requests = controller.get_favorites(message.from_user.id, 10)
    history = requests_to_string(requests)
    if len(history) == 0:
        bot.reply_to(message, text='Записи не найдены')
    else:
        history += '/load_favorite [Номер записи] - загрузить маршрут из избранного'
        bot.reply_to(message, text=history)


@bot.message_handler(commands=['load_last'])
def command_load_last(message):
    typed = message.text[11:]
    number = 0
    try:
        number = int(typed)
    except ValueError:
        if typed != '':
            bot.reply_to(message, text='Некорректные данные')
            return
    if not controller.load_last(message.from_user.id, number):
        bot.reply_to(message, text='Некорректные данные')
        return
    command_route(message)


@bot.message_handler(commands=['load_favorite'])
def command_load_favorite(message):
    typed = message.text[15:]
    number = 0
    try:
        number = int(typed)
    except ValueError:
        if typed != '':
            bot.reply_to(message, text='Некорректные данные')
            return
    if not controller.load_favorite(message.from_user.id, number):
        bot.reply_to(message, text='Некорректные данные')
        return
    command_route(message)


@bot.message_handler(commands=['route'])
def command_route(message):
    request = controller.get_current_request(message.from_user.id)
    keyboard = get_route_edit_keyboard()
    bot.send_message(chat_id=message.from_user.id,
                     text=request_to_string(request),
                     reply_markup=keyboard)


@bot.message_handler(commands=['admin'])
def command_admin(message):
    typed_password = message.text[7:]
    if typed_password == str(controller.get_admin_password()):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton('Изменить максимальное количество получаемых дорог с сайта',
                                                callback_data='edit_max_parsed_roads'),
                     types.InlineKeyboardButton('Получить историю запросов пользователя',
                                                callback_data='get_user_history'),
                     types.InlineKeyboardButton('Получить статистику уникальных пользователей',
                                                callback_data='get_unique_users'),
                     types.InlineKeyboardButton('Получить статистику использования бота',
                                                callback_data='get_usage_stats'))
        bot.send_message(chat_id=message.from_user.id, text=get_settings(), reply_markup=keyboard)
    else:
        bot.reply_to(message, text='Пароль \'' + str(typed_password) + '\' неправильный. В доступе отказано')


@bot.message_handler(func=lambda call: True)
def handle_random_message(message):
    bot.reply_to(message, start_message)


def start_update_progress_bar_async(progress, chat_id, message_id):
    i = 0
    while progress.value != progress.limit and i < 2000:
        text = progress.to_string()
        try:
            bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=text)
        except:
            pass
        time.sleep(1)
        i += 1
    bot.edit_message_text(message_id=message_id, chat_id=chat_id, text=progress.to_string())


@bot.callback_query_handler(func=lambda call: True)
def handle_callback(call):
    user_id = call.from_user.id
    request = controller.get_current_request(user_id)
    if call.data == 'switch_baggage':
        request.with_baggage = not request.with_baggage
    if call.data == 'switch_planes':
        request.switch_plane()
    if call.data == 'switch_trains':
        request.switch_train()
    if call.data == 'switch_buses':
        request.switch_bus()
    if call.data == 'switch_favorites':
        request.switch_favorite()
    if call.data == 'switch_baggage' \
            or call.data == 'switch_planes' \
            or call.data == 'switch_trains' \
            or call.data == 'switch_buses'  \
            or call.data == 'switch_favorites':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=request_to_string(request),
                              reply_markup=get_route_edit_keyboard())
    if call.data == 'add_town':
        message = bot.send_message(chat_id=call.message.chat.id,
                                   text="Введите город в формате:\n"
                                        "[Номер посещения] "
                                        "[Название] "
                                        "[Минимальное кол-во дней пребывания] "
                                        "[Максимальное количество дней пребывания]")
        bot.register_next_step_handler(message, add_town_to_request)
    if call.data == 'delete_town':
        message = bot.send_message(chat_id=call.message.chat.id,
                                   text="Введите город в формате:\n"
                                        "[Номер посещения] "
                                        "[Название] ")
        bot.register_next_step_handler(message, remove_town_from_request)
    if call.data == 'create_route':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)
        bot.send_message(call.message.chat.id, 'Подождите, идет поиск наилучшего маршрута...')
        request = controller.get_current_request(user_id)
        limit = 1
        for places in request.possible_places_lists:
            limit *= len(places)
        limit *= len(request.transport_types)
        progress = Progress(0, limit)
        bot_progress_bar_message = bot.send_message(call.message.chat.id, progress.to_string())
        chat_id = bot_progress_bar_message.chat.id
        message_id = bot_progress_bar_message.id
        th = Thread(target=start_update_progress_bar_async, args=(progress, chat_id, message_id), daemon=True)
        th.start()
        answer = controller.get_answer_to_user_route_request(user_id, progress)
        progress.value = limit
        text = answer_to_string(answer)
        if text != '':
            bot.send_message(call.message.chat.id, text)
            bot.send_photo(call.message.chat.id, photo=open(answer.pic, 'rb'), disable_notification=True)
            bot.send_photo(call.message.chat.id, photo=open(answer.map, 'rb'), disable_notification=True)
        else:
            bot.send_message(call.message.chat.id, 'Не найден маршрут')
    if call.data == 'add_town' \
            or call.data == 'delete_town':
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=request_to_string(request))
    if call.data == 'get_usage_stats':
        message = bot.send_message(chat_id=call.message.chat.id, text="Введите количество дней")
        bot.register_next_step_handler(message, get_usage_stats)
    if call.data == 'edit_max_parsed_roads':
        message = bot.send_message(chat_id=call.message.chat.id, text="Введите новое значение")
        bot.register_next_step_handler(message, set_max_parsed_roads_count)
    if call.data == 'get_user_history':
        message = bot.send_message(chat_id=call.message.chat.id, text="Введите id пользователя")
        bot.register_next_step_handler(message, get_history)
    if call.data == 'get_unique_users':
        message = bot.send_message(chat_id=call.message.chat.id, text="Введите количество дней")
        bot.register_next_step_handler(message, get_statistics)
    if call.data == 'edit_max_stored_roads' \
            or call.data == 'edit_max_parsed_roads' \
            or call.data == 'get_user_history' \
            or call.data == 'get_unique_users':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


def answer_to_string(answer: AnswerToUserRouteRequest) -> str:
    text = ''
    text += 'Найдено ' + str(answer.all_routes_count) + ' возможных маршрутов. '
    if answer.all_routes_count != 0:
        text += 'Вот самый дешевый из них: \n'
    i = 1
    for road in answer.low_cost_route:
        text += str(i) + ': ' + transport_type_to_string(road.transport_type) + ' из '
        text += road.departure_town + ' в ' + road.arrival_town
        text += ' (' + str(road.departure_time)[:16] + ' - ' + str(road.arrival_time)[:16] + ')'
        text += ' - ' + road.link + '\n'
        i += 1
    return text


def get_route_edit_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton('Добавить в избранное', callback_data='switch_favorites'),
                 types.InlineKeyboardButton('Включить/выключить багаж', callback_data='switch_baggage'),
                 types.InlineKeyboardButton('Показать/убрать самолеты', callback_data='switch_planes'),
                 types.InlineKeyboardButton('Показать/убрать поезда', callback_data='switch_trains'),
                 types.InlineKeyboardButton('Показать/убрать автобусы', callback_data='switch_buses'),
                 types.InlineKeyboardButton('Добавить город', callback_data='add_town'),
                 types.InlineKeyboardButton('Удалить город', callback_data='delete_town'),
                 types.InlineKeyboardButton('Построить маршрут', callback_data='create_route'))
    return keyboard


def remove_town_from_request(message):
    user_id = message.from_user.id
    request = controller.get_current_request(user_id)
    parts = message.text.split()
    if len(parts) != 2:
        bot.send_message(user_id, text='Некорректные данные')
        return
    if not request.remove_town(parts[0], parts[1]):
        bot.send_message(user_id, text='Некорректные данные')
        return
    bot.send_message(user_id,
                     text=request_to_string(controller.get_current_request(user_id)),
                     reply_markup=get_route_edit_keyboard())


def add_town_to_request(message):
    user_id = message.from_user.id
    request = controller.get_current_request(user_id)
    parts = message.text.split()
    if len(parts) != 4:
        bot.send_message(user_id, text='Некорректные данные')
        return
    if not request.add_town(parts[0], parts[1], parts[2], parts[3]):
        bot.send_message(user_id, text='Некорректные данные')
        return
    bot.send_message(user_id,
                     text=request_to_string(controller.get_current_request(user_id)),
                     reply_markup=get_route_edit_keyboard())


def transport_type_to_string(transport_type: TransportType):
    text = ''
    if transport_type == TransportType.PLANE:
        text += 'Самолет'
    elif transport_type == TransportType.TRAIN:
        text += 'Поезд'
    elif transport_type == TransportType.BUS:
        text += 'Автобус'
    return text


def request_to_string(request: UnfinishedRequest) -> str:
    text = ''
    text += "В избранном: "
    if request.is_favorite:
        text += 'Да'
    else:
        text += 'Нет'
    text += "\nВиды транспорта: "
    for transport_type in request.transport_types:
        text += transport_type_to_string(transport_type) + ' '
    text += '\n'
    text += "С багажом: "
    if request.with_baggage:
        text += 'Да' + '\n'
    else:
        text += 'Без разницы' + '\n'
    i = 1
    text += 'Список городов: \n'
    for places in request.possible_places_lists:
        text += str(i) + ": "
        for place in places:
            text += place.name
            text += '(' + str(place.min_stay_days) + '-'
            text += str(place.max_stay_days) + 'д); '
        text += '\n'
        i += 1
    return text


def convert_finished_to_unfinished_request(request: UserRequest):
    unfinished_request = UnfinishedRequest(request.user_id)
    unfinished_request.with_baggage = request.with_baggage
    unfinished_request.possible_places_lists = request.possible_places_lists
    unfinished_request.transport_types = request.transport_types
    unfinished_request.is_favorite = request.is_favorite
    return unfinished_request


def requests_to_string(requests: List[UserRequest]) -> str:
    history = ''
    for request in requests:
        history += request_to_string(convert_finished_to_unfinished_request(request)) + '\n'
    if history != '':
        history += '\n'
    return history


def get_settings() -> str:
    settings = controller.get_settings()
    output = ''
    output += 'Максимальное количество получаемых дорог с сайта: ' + str(settings[1]) + '\n'
    return output


def get_statistics(message):
    try:
        count = int(message.text)
        pic = controller.get_stats_picture(count)
        bot.send_photo(message.chat.id, photo=open(pic, 'rb'), disable_notification=True)
    except TypeError:
        bot.reply_to(message, 'Некорректные данные')


def get_history(message):
    history = requests_to_string(controller.get_history(message.text, 10))
    if len(history) == 0:
        bot.reply_to(message, text='Записи не найдены')
    else:
        bot.reply_to(message, text=history)


def get_usage_stats(message):
    try:
        count = int(message.text)
        pic = controller.get_usage_stats_picture(count)
        bot.send_photo(message.chat.id, photo=open(pic, 'rb'), disable_notification=True)
    except TypeError:
        bot.reply_to(message, 'Некорректные данные')


def set_max_parsed_roads_count(message):
    if not controller.set_max_count_parsed_roads(message.text):
        bot.reply_to(message, text='Некорректные данные')
    else:
        bot.reply_to(message, text='Значение изменено')


def run():
    bot.polling()
