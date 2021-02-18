import telebot
from telebot import types
from flask import Flask, request
from datetime import datetime

from map_api import get_location
from namaz_api import get_namaz, get_next
import service as s
import markups as m
import config
import db


def listener(messages):
    for message in messages:
        print(message.json)


user_find_city = dict()  # временный словарь для хранения найденного для пользователя местности
URL = 'https://cheel.pythonanywhere.com/' + config.SECRET
bot = telebot.TeleBot(config.BOT_TOKEN, skip_pending=True, threaded=False)
bot.set_update_listener(listener)
bot.remove_webhook()
bot.set_webhook(url=URL)

app = Flask(__name__)

@app.route('/'+config.SECRET, methods=['POST'])
def webhook():
    update = telebot.types.Update.de_json(request.stream.read().decode('utf-8'))
    bot.process_new_updates([update])
    return 'ok', 200


@bot.message_handler(commands=['start', 'help'])
def start(message: types.Message):
    # стартовое сообщение
    markup = m.get_main_markup()
    city = db.get_user_city(message.chat.id)  # получаем город пользователя, в виде кортежа(name, lat, lon)
    msg_text = s.get_text_main(message.chat.username, city[0].split(",")[0])
    bot.send_message(message.chat.id, text=msg_text, parse_mode='html', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text.split(' ')[0] == '🕌' or message.text.split(' ')[0] == '🕋',
                     content_types=['text'])
def day_handler(message: types.Message):
    # вывод времени намазав за текущую дату
    markup = m.get_main_markup()
    city = db.get_user_city(message.chat.id)
    timestamp = message.date
    if message.text.split(' ')[0] == '🕋':
        timestamp += 24*60*60
    date = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y')
    timings = get_namaz(date, city[1], city[2])
    msg_text = s.get_text_day(city[0].split(",")[0], date, timings)
    bot.send_message(message.chat.id, text=msg_text, parse_mode='html', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '🌍 Место', content_types=['text'])
def city_handler(message: types.Message):
    # смена местности
    markup = types.ReplyKeyboardRemove()
    msg = bot.send_message(message.chat.id, text="Введите название населенного пункта для поиска",
                           reply_markup=markup)
    # указываем следующий шаг (def ask_place) после ввода пользователя
    bot.register_next_step_handler(msg, ask_place)


def ask_place(message):
    global user_find_city
    # запрашиваем ввод местности до тех пор пока не будет найден только один отвечающий запросу вариант
    chat_id = message.chat.id
    text = message.text
    # поиск местности
    location = get_location(text)
    if location is None:  # не найдено локации
        msg = bot.send_message(chat_id, 'Ничего не найдено. Проверьте правильность написания пункта, или попробуйте'
                                        ' ввести ближайщий крупный населенный пункт')
        bot.register_next_step_handler(msg, ask_place)  # повторно запрашиваем ввод местности
        return
    if not location:  # ошибка во время поиска
        msg = bot.send_message(chat_id, 'Ошибка во время поиска местности, попробуйте еще раз.\n '
                                        'Спасибо')
        bot.register_next_step_handler(msg, ask_place)  # повторно запрашиваем ввод местности
        return
    if len(location) != 1:  # найдена больше чем одна локация
        msg = bot.send_message(chat_id, 'Найденно несколько вариантов, уточните положение, '
                                        'например указав область или страну')
        bot.register_next_step_handler(msg, ask_place)  # повторно запрашиваем ввод местности
        return

    markup = m.city_confirm_dialog()

    # записываем локацию в базу, если ее там нет
    db.write_city((location[0]['display_name'], float(location[0]['lat']), float(location[0]['lon'])))
    # получаем id локации из базы и временно присваеваем ее пользователю
    city_id = db.get_city_id_by_name(location[0]['display_name'])
    user_find_city[chat_id] = city_id
    # спрашиваем пользователя верно найдена локация или нет
    bot.send_message(chat_id, location[0]['display_name'], reply_markup=markup)


@bot.callback_query_handler(func=lambda call: call.data == 'yes_city')
def yes_city_inline(call):
    """если местность найдена верно"""
    chat_id = call.message.chat.id
    # записываем в базу выбранный город и очищаем временную запись
    db.set_user_city(chat_id, int(user_find_city[chat_id]))
    user_find_city.pop(chat_id, None)

    city = db.get_user_city(chat_id)
    msg_text = f'{call.message.chat.username}, ваше местоположение установленно как {city[0].split(",")[0]}'

    bot.edit_message_text(chat_id=chat_id, message_id=call.message.message_id,
                          text=msg_text)
    start(call.message)


@bot.callback_query_handler(func=lambda call: call.data == 'no_city')
def no_city_inline(call):
    """если не та местность, запускаем еще раз поиск местности"""
    # убираем кнопки у сообщения
    bot.edit_message_reply_markup(chat_id=call.message.chat.id, message_id=call.message.message_id,)
    # очищаем временную запись о найденном городе
    user_find_city.pop(call.message.chat.id, None)
    # запуск поиска
    city_handler(call.message)


@bot.message_handler(func=lambda message: message.text == '⏰ Следующий')
def next_handler(message: types.Message):
    """время следующего намаза"""
    markup = m.get_main_markup()
    city = db.get_user_city(message.chat.id)
    timestamp = message.date
    namaz = get_next(timestamp, city[1], city[2])
    msg_text = s.get_text_next(city[0].split(",")[0], namaz)
    bot.send_message(message.chat.id, text=msg_text, parse_mode='html', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '📆 На дату', content_types=['text'])
def date_handler(message: types.Message):
    """время намазов на определенную дату"""
    markup = types.ReplyKeyboardRemove()
    msg_text = s.get_text_date()
    msg = bot.send_message(message.chat.id, text=msg_text, parse_mode='html', reply_markup=markup)
    # указываем следующий шаг (def ask_date) после ввода пользователем даты
    bot.register_next_step_handler(msg, ask_date)


def ask_date(message):
    markup = m.get_main_markup()
    chat_id = message.chat.id
    text = message.text
    city = db.get_user_city(chat_id)
    try:  # проверка введенной даты на валидность
        valid_date = datetime.strptime(text, '%d.%m.%Y')
    except ValueError:
        bot.send_message(chat_id, text='Дата введена неверно', reply_markup=markup)
        return
    else:
        date = valid_date.strftime('%d-%m-%Y')
        timings = get_namaz(date, city[1], city[2])
        msg_text = s.get_text_day(city[0].split(",")[0], date, timings)
        bot.send_message(message.chat.id, text=msg_text, parse_mode='html', reply_markup=markup)


@bot.message_handler(func=lambda message: message.text == '⁉️Помощь', content_types=['text'])
def help_handler(message: types.Message):
    start(message)


#TODO Клавиатура всегда развернута
#TODO правильная выдача следующего намаза, не верно из за timezone
