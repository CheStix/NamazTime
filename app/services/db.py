import sqlite3
import aiosqlite

DEFAULT_CITY = (
    'Москва, Центральный федеральный округ, Россия',
    55.7504461,
    37.6174943,
    3
)


def ensure_connection(func):
    # защищенное соединение с базой данных
    async def inner(*args, **kwargs):
        async with aiosqlite.connect('db.sqlite3') as conn:
            res = await func(*args, conn=conn, **kwargs)
        return res
    return inner


@ensure_connection
async def init_db(conn, force: bool = False):
    """
    Проверяем что нужные таблицы в базе данных существуют, если нет то создаем их
    :param force: пересоздать таблицы
    :param conn: соединение с базой передаваемое через декоратор
    """

    c = await conn.cursor()

    # Удаляем таблицы городов и пользователей, если передан параметр Force=True
    if force:
        await c.execute('DROP TABLE IF EXISTS cities')
        await c.execute('DROP TABLE IF EXISTS users')

    # Создаем таблицу городов если ее нет
    await c.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL UNIQUE,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            timezone REAL NOT NULL 
        )
    ''')

    # Создаем таблицу пользователей если ее нет
    await c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE ON CONFLICT REPLACE,
            city_id INTEGER NOT NULL,
            FOREIGN KEY (city_id) REFERENCES cities (id)
        )
    ''')
    # Записываем в  таблицу cities населенный пунк DEFAULT_CITY
    try:
        await c.execute("""INSERT OR IGNORE INTO cities (city_name, latitude, longitude, timezone) 
                    VALUES (?, ?, ?, ?)""", DEFAULT_CITY)
    except aiosqlite.DatabaseError as e:
        print('Error: ', e)

    await conn.commit()


@ensure_connection
async def set_user_city(user_id: int, city_id: int, conn):
    """
    Устанавливаем пользователю в соответствие id выбранного города
    :param conn: соединение с базой передаваемое через декоратор
    :param user_id: telegram id пользователя
    :param city_id: id города из таблицы cities
    :return:
    """
    c = await conn.cursor()
    await c.execute("""INSERT INTO users (user_id, city_id) 
                    VALUES (?, ?)""",
              (user_id, city_id)
              )
    await conn.commit()


@ensure_connection
async def get_user_city(user_id: int, conn) -> tuple:
    """
    получаем город с координатами для пользователя
    :param user_id: telegram id пользователя
    :param conn: соединение с базой передаваемое через декоратор
    :return: tuple (city_name, latitude, longitude)
    """
    c = await conn.cursor()
    await c.execute("""
                SELECT city_name, latitude, longitude, timezone
                FROM users
                inner join cities on cities.id = users.city_id
                WHERE user_id = ?
                """,
              (user_id,))
    city = await c.fetchone()
    if city is None:
        # если нет пользователя, то записываем его в базу и устанавливаем город по умолчанию
        city_id = await get_city_id_by_name(DEFAULT_CITY[0])
        await set_user_city(user_id, city_id)
        return DEFAULT_CITY
    else:
        return city


@ensure_connection
async def write_city(*data, conn):
    """
    Записываем в  таблицу cities населенный пунк с  кортежем data
    :param conn: connection to db
    :param data: кортеж из именем места и его координатами
    """
    c = await conn.cursor()
    try:
        await c.execute("""INSERT OR IGNORE INTO cities (city_name, latitude, longitude, timezone) 
                    VALUES (?, ?, ?, ?)""", data)
    except aiosqlite.DatabaseError as e:
        print('Error: ', e)
    else:
        await conn.commit()


@ensure_connection
async def get_city_id_by_name(name: str, conn):
    """
    получаем id города в таблице cities по имени
    :param conn: connection to db
    :param name: название города
    :return: int id of city
    """
    c = await conn.cursor()
    await c.execute('SELECT id FROM cities WHERE city_name = ?', (name,))
    city_id, = await c.fetchone()
    return city_id


@ensure_connection
async def delete_user(user_id: int, conn):
    """
    удаление записи из таблицы для пользователя с переданным user_id
    :param user_id: id пользователя
    :param conn: соединение с базой
    :return:
    """
    c = await conn.cursor()

    try:
        await c.execute("""DELETE FROM users WHERE user_id=?""", (user_id,))
    except aiosqlite.DatabaseError as e:
        print('Error: ', e)
    else:
        await conn.commit()


if __name__ == '__main__':
    pass
    # init_db(force=True)
    # write_city(data=DEFAULT_CITY)
