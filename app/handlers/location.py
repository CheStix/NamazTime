from aiogram import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import StatesGroup, State
from aiogram.types import Message, ReplyKeyboardRemove, CallbackQuery

from .common import cmd_start_help
from ..keyboards.markups import city_confirm_dialog, get_main_markup
from ..services import db
from ..services.map_api import get_loc_geocode, get_loc_timezone

MAIN_MARKUP = get_main_markup()


class SetLocation(StatesGroup):
    waiting_loc_name = State()
    confirm_loc_name = State()


async def location_start(message: Message):
    await message.answer(text='Введите название населенного пункта для поиска', reply_markup=ReplyKeyboardRemove())
    await SetLocation.waiting_loc_name.set()


async def location_search(message: Message, state: FSMContext):
    response = await get_loc_geocode(message.text)
    # не найдено локации
    if response['status'] is None:
        msg = 'Ничего не найдено. Проверьте правильность написания пункта, или попробуйте ' \
              'ввести ближайший крупный населенный пункт'
        await message.answer(msg)
        return
    # найдена больше чем одна локация
    elif response['status'] == 'Multiple':
        msg = 'Найдено несколько вариантов, уточните положение, ' \
              'например указав область или страну'
        await message.answer(msg)
        return
    # ошибка во время поиска
    elif response['status'] == 'Error':
        msg = 'Ошибка во время поиска местности, попробуйте еще раз.\n ' \
              'Спасибо'
        await message.answer(msg)
        return

    markup = city_confirm_dialog()
    await state.update_data(response)
    await message.answer(response['display_name'], reply_markup=markup)
    await SetLocation.confirm_loc_name.set()


async def location_confirm(call: CallbackQuery, state: FSMContext):
    answer = call.data.split('_')[0]
    if answer == 'no':
        msg = 'Попробуем еще раз.\nВведите название населенного пункта для поиска'
        await call.message.edit_text(msg)
        await SetLocation.waiting_loc_name.set()
    if answer == 'yes':
        location = await state.get_data()
        lat = float(location['lat'])
        lon = float(location['lon'])
        timezone = await get_loc_timezone(lat, lon)  #TODO обработать False
        await db.write_city(location['display_name'], lat, lon, timezone)
        city_id = await db.get_city_id_by_name(location['display_name'])
        await db.set_user_city(call.message.chat.id, city_id)
        msg = f'{call.message.chat.username}, ваше местоположение установленно как ' \
              f'{location["display_name"].split(",")[0]}'
        await call.message.edit_text(msg)
        await cmd_start_help(call.message, state)
    await call.answer()


def register_handlers_location(dp: Dispatcher):
    dp.register_message_handler(location_start, Text(startswith='🌍'), state='*')
    dp.register_message_handler(location_search, state=SetLocation.waiting_loc_name)
    dp.register_callback_query_handler(location_confirm, Text(endswith='city'), state=SetLocation.confirm_loc_name)
