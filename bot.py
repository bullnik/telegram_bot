from typing import List

import telebot
from telebot import types
import controller
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


@bot.message_handler(commands=['start', 'help'])
def command_help(message):
    bot.reply_to(message, start_message)


def get_route_edit_keyboard():
    keyboard = types.InlineKeyboardMarkup(row_width=1)
    keyboard.add(types.InlineKeyboardButton('Включить/выключить багаж', callback_data='1'),
                 types.InlineKeyboardButton('Показать/убрать самолеты', callback_data='2'),
                 types.InlineKeyboardButton('Показать/убрать поезда', callback_data='3'),
                 types.InlineKeyboardButton('Показать/убрать автобусы', callback_data='4'),
                 types.InlineKeyboardButton('Добавить город', callback_data='5'),
                 types.InlineKeyboardButton('Удалить город', callback_data='6'),
                 types.InlineKeyboardButton('Построить маршрут', callback_data='7'))
    return keyboard


@bot.message_handler(commands=['route'])
def command_route(message):
    request = controller.get_current_request(message.from_user.id)
    keyboard = get_route_edit_keyboard()
    bot.send_message(chat_id=message.from_user.id,
                     text=request_to_string(request),
                     reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def command_admin_callback(call):
    user_id = call.from_user.id
    request = controller.get_current_request(user_id)
    if call.data == '1':
        request.with_baggage = not request.with_baggage
    elif call.data == '2':
        request.switch_plane()
    elif call.data == '3':
        request.switch_train()
    elif call.data == '4':
        request.switch_bus()

    if call.data == '5':
        message = bot.send_message(chat_id=call.message.chat.id,
                                   text="Введите город в формате:\n"
                                        "[Номер посещения] "
                                        "[Название] "
                                        "[Минимальное кол-во дней пребывания] "
                                        "[Максимальное количество дней пребывания]")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=request_to_string(request))
        bot.register_next_step_handler(message, add_town_to_request)
    elif call.data == '6':
        message = bot.send_message(chat_id=call.message.chat.id,
                                   text="Введите город в формате:\n"
                                        "[Номер посещения] "
                                        "[Название] ")
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=request_to_string(request))
        bot.register_next_step_handler(message, remove_town_from_request)
    else:
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text=request_to_string(request),
                              reply_markup=get_route_edit_keyboard())


def remove_town_from_request(message):
    user_id = message.from_user.id
    request = controller.get_current_request(user_id)
    parts = message.text.split()
    if len(parts) != 3:
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


def request_to_string(request: UnfinishedRequest) -> str:
    text = ''
    # text += "Id пользователя: " + str(request.user_id) + '\n'
    text += "Виды транспорта: "
    for transport_type in request.transport_types:
        if transport_type == TransportType.PLANE:
            text += 'Самолет '
        elif transport_type == TransportType.TRAIN:
            text += 'Поезд '
        elif transport_type == TransportType.BUS:
            text += 'Автобус '
    text += '\n'
    text += "Багаж: " + str(request.with_baggage) + '\n'
    i = 1
    for places in request.possible_places_lists:
        text += str(i) + ": "
        for place in places:
            text += place.name
            text += '(' + str(place.min_stay_days) + '-'
            text += str(place.max_stay_days) + 'д); '
        text += '\n'
        i += 1
    return text


@bot.message_handler(commands=['favorites'])
def command_favourites(message):
    requests = controller.get_favorites(message.from_user.id, 10)
    history = requests_to_string(requests)
    if len(history) == 0:
        bot.reply_to(message, text='Записи не найдены')
    else:
        bot.reply_to(message, text=history)


def requests_to_string(requests: List[UserRequest]) -> str:
    history = ''
    for request in requests:
        history += 'Id пользователя: ' + str(request.user_id) + '\n'\
                     'С багажом: ' + str(request.with_baggage) + '\n'\
                     'Типы транспорта: ' + str(request.transport_types) + '\n'\
                     'Списки городов: ' + '\n'
        for places_list in request.possible_places_lists:
            history += '- ' + str(places_list) + '\n'
    return history


@bot.message_handler(commands=['admin'])
def command_admin(message):
    typed_password = message.text[7:]
    if typed_password == str(controller.get_admin_password()):
        keyboard = types.InlineKeyboardMarkup(row_width=1)
        keyboard.add(types.InlineKeyboardButton('Изменить максимальное количество дорог в базе данных',
                                                callback_data='1'),
                     types.InlineKeyboardButton('Изменить максимальное количество получаемых дорог с сайта',
                                                callback_data='2'),
                     types.InlineKeyboardButton('Получить историю запросов пользователя',
                                                callback_data='3'),
                     types.InlineKeyboardButton('Получить статистику уникальных пользователей',
                                                callback_data='4'))
        bot.send_message(chat_id=message.from_user.id, text=get_settings(), reply_markup=keyboard)
    else:
        bot.reply_to(message, text='Пароль: ' + str(typed_password) + ' неправильный. В доступе отказано')


def get_settings() -> str:
    settings = controller.get_settings()
    output = ''
    output += 'Максимальное количество дорог в базе данных: ' + str(settings[0]) + '\n'
    output += 'Максимальное количество получаемых дорог с сайта: ' + str(settings[1]) + '\n'
    return output


@bot.callback_query_handler(func=lambda call: True)
def command_admin_callback(call):
    if call.data == '1':
        message = bot.send_message(chat_id=call.message.chat.id, text="Введите новое значение")
        bot.register_next_step_handler(message, set_max_saved_roads_count)
    elif call.data == '2':
        message = bot.send_message(chat_id=call.message.chat.id, text="Введите новое значение")
        bot.register_next_step_handler(message, set_max_parsed_roads_count)
    elif call.data == '3':
        message = bot.send_message(chat_id=call.message.chat.id, text="Введите id пользователя")
        bot.register_next_step_handler(message, get_history)
    elif call.data == '4':
        message = bot.send_message(chat_id=call.message.chat.id, text="Введите количество дней")
        bot.register_next_step_handler(message, get_statistics)
    else:
        raise NotImplemented
    bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


def get_statistics(message):
    try:
        count = int(message.text)
        bot.send_photo(message.chat.id, controller.get_stats_picture(count))
    except TypeError:
        bot.reply_to(message, 'Некорректные данные')


def get_history(message):
    history = requests_to_string(controller.get_history(message.text, 10))
    if len(history) == 0:
        bot.reply_to(message, text='Записи не найдены')
    else:
        bot.reply_to(message, text=history)


def set_max_saved_roads_count(message):
    if not controller.set_max_count_parsed_roads(message.text):
        bot.reply_to(message, text='Некорректные данные')
    else:
        bot.reply_to(message, text='Значение изменено')


def set_max_parsed_roads_count(message):
    if not controller.set_max_saved_roads_count(message.text):
        bot.reply_to(message, text='Некорректные данные')
    else:
        bot.reply_to(message, text='Значение изменено')


@bot.message_handler(commands=['history'])
def command_history(message):
    requests = controller.get_history(message.from_user.id, 10)
    history = requests_to_string(requests)
    if len(history) == 0:
        bot.reply_to(message, text='Записи не найдены')
    else:
        bot.reply_to(message, text=history)


@bot.message_handler(func=lambda call: True)
def handle_random_message(message):
    bot.reply_to(message, start_message)


def run():
    bot.polling()
