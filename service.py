
def get_text_main(user, city):
    t = f'Ас-саламу алейкум, <strong>{user}</strong>\n' \
        f'Местоположение: <strong>{city}</strong>\n' \
        f'<strong>"Сегодня"</strong> - время намазов на сегодня\n' \
        f'<strong>"Завтра"</strong> - время намазов на завтра\n' \
        f'<strong>"На дату"</strong> - время намазов на выбранную дату\n' \
        f'<strong>"Место"</strong> - выбор населеного пункта по которому будет выдаваться информация\n' \
        f'<strong>"Помощь"</strong> - помощь по боту\n'
    return t


def get_text_day(city, date, timings):
    if timings is not None:
        t = f'<strong>{city} {date}</strong>\n' \
            f'<code>ФАДЖР  - {timings["Fajr"]}</code>\n' \
            f'<code>ШУРУК  - {timings["Sunrise"]}</code>\n' \
            f'<code>ЗУХР   - {timings["Dhuhr"]}</code>\n' \
            f'<code>АСР    - {timings["Asr"]}</code>\n' \
            f'<code>МАГРИБ - {timings["Maghrib"]}</code>\n' \
            f'<code>ИША    - {timings["Isha"]}</code>\n'
    else:
        t = 'Ошибка загрузки данных, попробуйте еще раз.\n' \
            'Спасибо.'
    return t


def get_text_next(city: str, namaz: tuple) -> str:
    namaze_name = {"Fajr": 'ФАДЖР', 'Dhuhr': 'ЗУХР', 'Asr': 'АСР', 'Maghrib': 'МАГРИБ', 'Isha': 'ИША'}
    t = f'<strong>{city}</strong>, следующий намаз:\n' \
        f'<strong>{namaz[2]}</strong>\n' \
        f'<code>{namaze_name[namaz[0]]}  - {namaz[1]}</code>\n'
    return t


def get_text_date():
    t = "Введите дату, на которую желаете получить расписание намазов\n" \
        "<strong>Формат: <i>дд.мм.гггг</i></strong>"
    return t
