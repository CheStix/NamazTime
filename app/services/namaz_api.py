from datetime import datetime, timedelta

from aiohttp import ClientSession

URL_MAIN = 'http://api.aladhan.com/v1/timings'
NAMAZ = ('Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha')


async def get_namaz(date: str, lat: float, lon: float) -> dict:
    """
    время намазов для местности на дату
    :param date: дата в виде 'DD-MM-YYYY'
    :param lat: широта
    :param lon: долгота
    :return:
    """
    url = f'{URL_MAIN}/{date}?latitude={lat}&longitude={lon}&method=2'
    async with ClientSession() as session:
        async with session.get(url) as resp:
            r = await resp.json()
    return r['data']['timings']


async def get_next(timestamp: datetime, lat: float, lon: float) -> tuple:
    """
    время следующего намаза для местности относительно переданного timestamp
    :param timestamp: timestamp времени
    :param lat: широта
    :param lon: долгота
    :return: tuple (название_намаза, время_намаза, дата_намаза)
    """
    date = timestamp.strftime('%d-%m-%Y')
    timings = await get_namaz(date, lat, lon)
    for k in NAMAZ:
        t = datetime.strptime(f'{timings[k]} {date}', '%H:%M %d-%m-%Y')
        if t > timestamp:
            return k, timings[k], date
    timestamp += timedelta(days=1)
    date = timestamp.strftime('%d-%m-%Y')
    timings = await get_namaz(date, lat, lon)
    return 'Fajr', timings['Fajr'], date


if __name__ == '__main__':
    pass
    # date = datetime.now()
    # r = get_namaz(date.strftime('%d-%m-%Y'), 42.9830241, 47.5048717,)
    # r = get_next(date, 42.9830241, 47.5048717)
    # print(r)
