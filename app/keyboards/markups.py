from aiogram import types


def city_confirm_dialog() -> types.InlineKeyboardMarkup:
    """
    inline диалог подтверждения города
    """
    yes_btn = types.InlineKeyboardButton(text="Да", callback_data="yes_city")
    no_btn = types.InlineKeyboardButton(text="Нет", callback_data="no_city")
    markup = types.InlineKeyboardMarkup()
    markup.add(yes_btn, no_btn)
    return markup


def get_main_markup() -> types.ReplyKeyboardMarkup:
    """
    главная клавиатура бота
    """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    next_btn = types.KeyboardButton(text="⏰ Следующий")
    today_btn = types.KeyboardButton(text="🕌 Сегодня")
    date_btn = types.KeyboardButton(text='📆 На дату')
    tomorrow_btn = types.KeyboardButton(text="🕋 Завтра")
    city_btn = types.KeyboardButton(text="🌍 Место")
    help_btn = types.KeyboardButton(text="⁉️Помощь")
    markup.add(today_btn, next_btn, tomorrow_btn)
    markup.add(date_btn, city_btn, help_btn)
    return markup
