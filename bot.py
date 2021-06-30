import telebot
import pasta
import vk_parser
from telebot import types

token = "801332145:AAGpj1_4Pm4WtjdDi8QsRxdb0F3GaShGr_M"  # @chimberbembra_bot
bot = telebot.TeleBot(token)


def write_start_message(message):
    bot.reply_to(message,
                 "Используйте следующие команды:\n"
                 "/help - помощь\n"
                 "/name [id] - получить имя человека ВКонтакте по его id\n"
                 "/test - тест\n"
                 "Или напишите \"Я бычара\"")


@bot.message_handler(commands=['test'])
def command_test(message):


    bot.reply_to(message, "fdsafdasfdsa")


@bot.message_handler(commands=['start', 'help'])
def command_help(message):
    write_start_message(message)


@bot.message_handler(commands=['name'])
def command_help(message):
    vk_id = message.text[6:]
    name = vk_parser.parse(vk_id)
    bot.reply_to(message, 'id: ' + vk_id + '\n' + 'Имя: ' + name)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if message.text == "Я бычара":
        answer_bik(message)
    else:
        bot.reply_to(message, pasta.get_random_pasta())


def answer_bik(message):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton("Да", callback_data='yes')
    key_no = types.InlineKeyboardButton("Нет", callback_data='no')
    keyboard.add(key_yes)
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, text="Ахуел?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == 'no' or call.data == 'yes':
        keyboard = types.InlineKeyboardMarkup()
        key = types.InlineKeyboardButton("Пойти нахуй", callback_data='go')
        keyboard.add(key)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text="Пошел нахуй тогда", reply_markup=keyboard)
    elif call.data == 'go':
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


def run():
    bot.polling()
