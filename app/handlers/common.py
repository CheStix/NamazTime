from datetime import timedelta

from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.types import Message, CallbackQuery

from ..keyboards.aiogram_calendar.simple_calendar import calendar_callback as simple_cal_callback, SimpleCalendar
from ..services import db
from ..services import msg_templates
from ..keyboards.markups import get_main_markup
from ..services.namaz_api import get_namaz, get_next

MAIN_MARKUP = get_main_markup()


async def cmd_start_help(message: Message, state: FSMContext):
    await state.finish()
    city = await db.get_user_city(message.chat.id)
    msg = msg_templates.get_text_main(message.chat.username, city[0].split(',')[0])
    await message.answer(text=msg, reply_markup=MAIN_MARKUP)


async def day_handler(message: Message):
    # обработчик кнопок "🕌 Сегодня" и "🕋 Завтра"
    city = await db.get_user_city(message.from_user.id)
    timestamp = message.date + timedelta(hours=city[3])
    if message.text.startswith('🕋'):
        timestamp += timedelta(days=1)
    date = timestamp.strftime('%d-%m-%Y')
    timings = await get_namaz(date, city[1], city[2])
    if timings is None:
        msg = 'Ошибка загрузки данных, попробуйте еще раз.\nСпасибо.'
    else:
        msg = msg_templates.get_text_day(city[0].split(',')[0], date, timings)
    await message.answer(text=msg, reply_markup=MAIN_MARKUP)


async def date_handler(message: Message):
    # вывод клавиатуры выбора даты
    await message.answer('Please select a date: ', reply_markup=await SimpleCalendar().start_calendar())


async def next_handler(message: Message):
    city = await db.get_user_city(message.from_user.id)
    timestamp = message.date + timedelta(hours=city[3])
    namaz = await get_next(timestamp, city[1], city[2])
    msg = msg_templates.get_text_next(city[0].split(",")[0], namaz)
    await message.answer(text=msg, reply_markup=MAIN_MARKUP)


async def process_simple_calendar(callback_query: CallbackQuery, callback_data: dict):
    # выбор даты и выдача времени намаза
    selected, date = await SimpleCalendar().process_selection(callback_query, callback_data)
    if selected:
        city = await db.get_user_city(callback_query.from_user.id)
        date = date.strftime('%d-%m-%Y')
        timings = await get_namaz(date, city[1], city[2])
        msg_text = msg_templates.get_text_day(city[0].split(',')[0], date, timings)
        await callback_query.message.answer(msg_text, reply_markup=MAIN_MARKUP)


def register_handlers_common(dp: Dispatcher, admin_id: int):
    dp.register_message_handler(cmd_start_help, commands=['start', 'help'], state='*')
    dp.register_message_handler(cmd_start_help, Text(startswith='⁉', ignore_case=True), state='*')
    dp.register_message_handler(day_handler, Text(startswith=['🕌', '🕋']), state='*')
    dp.register_message_handler(date_handler, Text(startswith='📆'), state='*'),
    dp.register_callback_query_handler(process_simple_calendar, simple_cal_callback.filter(),state='*')
    dp.register_message_handler(next_handler, Text(startswith='⏰'), state='*')
