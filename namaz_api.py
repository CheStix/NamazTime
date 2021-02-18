from datetime import datetime

import requests
import time

URL_MAIN = 'http://api.aladhan.com/v1/timings'
NAMAZ = ('Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha')


def get_namaz(date: str, lat: float, lon: float) -> dict:
    """
    время намазов для местности на дату
    :param date: дата ввиде 'DD-MM-YYYY'
    :param lat: широта
    :param lon: долгота
    :return:
    """
    url = f'{URL_MAIN}/{date}?latitude={lat}&longitude={lon}&method=2'
    try:
        r = requests.get(url)
    except:
        r = None
    else:
        r = r.json()['data']['timings']
    return r


def get_next(timestamp: int, lat: float, lon: float) -> tuple:
    """
    время следующего намаза для местности относительно переденного timestamp
    :param timestamp: timestamp времени
    :param lat: широта
    :param lon: долгота
    :return: tuple (название_намаза, время_намаза, дата_намаза)
    """
    date = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y')
    timings = get_namaz(date, lat, lon)
    for k in NAMAZ:
        t = datetime.strptime(f'{timings[k]} {date}', '%H:%M %d-%m-%Y').timestamp()
        if int(t) > timestamp:
            return k, timings[k], date
    timestamp += 24*60*60
    date = datetime.fromtimestamp(timestamp).strftime('%d-%m-%Y')
    timings = get_namaz(date, lat, lon)
    return 'Fajr', timings['Fajr'], date


if __name__ == '__main__':
    date = time.time()
    r = get_namaz(date, 42.9830241, 47.5048717,)
    r = get_next(1589460303, 42.9830241, 47.5048717)
    print(r)
