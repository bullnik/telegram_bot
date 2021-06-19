import telebot
import pasta
import vkparser
from telebot import types

token = "801332145:AAGpj1_4Pm4WtjdDi8QsRxdb0F3GaShGr_M"
bot = telebot.TeleBot(token)


@bot.message_handler(commands=['start'])
def command_help(message):
    bot.reply_to(message, "Я - бычарный бот.\n/help - помощь\n/parse [ссылка] - запарсить сайтец")


@bot.message_handler(commands=['help'])
def command_help(message):
    bot.reply_to(message, "Напишите \"Я бычара\"")


@bot.message_handler(commands=['parse'])
def command_help(message):
    vk_id = message.text[7:]
    name = vkparser.parse(vk_id)
    bot.reply_to(message, 'id: ' + vk_id + '\n' + 'Имя: ' + name)


@bot.message_handler(func=lambda m: True)
def echo_all(message):
    if message.text == "Я бычара":
        answer_bik(message)
    else:
        bot.reply_to(message, pasta.get_random_pasta())


def answer_bik(message):
    keyboard = types.InlineKeyboardMarkup()
    key_yes = types.InlineKeyboardButton("Да", callback_data="poslan")
    key_no = types.InlineKeyboardButton("Нет", callback_data="poslan")
    keyboard.add(key_yes)
    keyboard.add(key_no)
    bot.send_message(message.from_user.id, text="Ахуел?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: True)
def callback_worker(call):
    if call.data == "poslan":
        keyboard = types.InlineKeyboardMarkup()
        key = types.InlineKeyboardButton("Пойти нахуй", callback_data="poshel naxyi")
        keyboard.add(key)
        bot.edit_message_text(chat_id=call.message.chat.id, message_id=call.message.id,
                              text="Пошел нахуй тогда", reply_markup=keyboard)
    elif call.data == "poshel naxyi":
        bot.delete_message(chat_id=call.message.chat.id, message_id=call.message.id)


def run():
    bot.polling()
