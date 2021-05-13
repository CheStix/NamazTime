import sqlite3

DEFAULT_CITY = (
    'Москва, Центральный административный округ, Москва, Центральный федеральный округ, Россия',
    55.7504461,
    37.6174943
)


def ensure_connection(func):
    # защищенное соединение с базой данных
    def inner(*args, **kwargs):
        with sqlite3.connect('db.sqlite3') as conn:
            res = func(*args, conn=conn, **kwargs)
        return res
    return inner


@ensure_connection
def init_db(conn, force: bool = False):
    """
    Проверяем что нужные таблицы в базе данных существуют, если нет то создаем их
    :param force: пересоздать таблицы
    :param conn: соединение с базой передаваемое через декоратор
    """

    c = conn.cursor()

    # Удаляем таблицы городов и пользователей, если передан параметр Force=True
    if force:
        c.execute('DROP TABLE IF EXISTS cities')
        c.execute('DROP TABLE IF EXISTS users')

    # Создаем таблицу городов если ее нет
    c.execute('''
        CREATE TABLE IF NOT EXISTS cities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city_name TEXT NOT NULL UNIQUE,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL 
        )
    ''')

    # Создаем таблицу пользователей если ее нет
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL UNIQUE ON CONFLICT REPLACE,
            city_id INTEGER NOT NULL,
            FOREIGN KEY (city_id) REFERENCES cities (id)
        )
    ''')
    # Записываем в  таблицу cities населенный пунк DEFAULT_CITY
    try:
        c.execute("""INSERT OR IGNORE INTO cities (city_name, latitude, longitude) 
                    VALUES (?, ?, ?)""", DEFAULT_CITY)
    except sqlite3.DatabaseError as e:
        print('Error: ', e)

    conn.commit()


@ensure_connection
def set_user_city(user_id: int, city_id: int, conn):
    """
    Устанавливаем пользователю в соответствие id выбранного города
    :param conn: соединение с базой передаваемое через декоратор
    :param user_id: telegram id пользователя
    :param city_id: id города из таблицы cities
    :return:
    """
    c = conn.cursor()
    c.execute("""INSERT INTO users (user_id, city_id) 
                    VALUES (?, ?)""",
              (user_id, city_id)
              )
    conn.commit()


@ensure_connection
def get_user_city(user_id: int, conn) -> tuple:
    """
    получаем город с координатами для пользователя
    :param user_id: telegram id пользователя
    :param conn: соединение с базой передаваемое через декоратор
    :return: tuple (city_name, latitude, longitude)
    """
    c = conn.cursor()
    c.execute("""
                SELECT city_name, latitude, longitude
                FROM users
                inner join cities on cities.id = users.city_id
                WHERE user_id = ?
                """,
              (user_id,))
    city = c.fetchone()
    if city is None:
        # если нет пользователя, то записываем его в базу и устанавливаем город по умолчанию
        city_id = get_city_id_by_name(DEFAULT_CITY[0])
        set_user_city(user_id, city_id)
        return DEFAULT_CITY
    else:
        return city


@ensure_connection
def write_city(data, conn):
    """
    Записываем в  таблицу cities населенный пунк с  кортежем data
    :param conn: connection to db
    :param data: кортеж из именем места и его координатами
    """
    c = conn.cursor()
    try:
        c.execute("""INSERT OR IGNORE INTO cities (city_name, latitude, longitude) 
                    VALUES (?, ?, ?)""", data)
    except sqlite3.DatabaseError as e:
        print('Error: ', e)
    else:
        conn.commit()


@ensure_connection
def get_city_id_by_name(name: str, conn):
    """
    получаем id города в таблице cities по имени
    :param conn: connection to db
    :param name: название города
    :return: int id of city
    """
    c = conn.cursor()
    c.execute('SELECT id FROM cities WHERE city_name = ?', (name,))
    city_id, = c.fetchone()
    return city_id


@ensure_connection
def delete_user(user_id: int, conn):
    """
    удлаения записи из таблицы для пользователя с переданным user_id
    :param user_id: id пользователя
    :param conn: соединение с базой
    :return:
    """
    c = conn.cursor()

    try:
        c.execute("""DELETE FROM users WHERE user_id=?""", (user_id,))
    except sqlite3.DatabaseError as e:
        print('Error: ', e)
    else:
        conn.commit()


if __name__ == '__main__':
    init_db(force=True)
    write_city(data=DEFAULT_CITY)


