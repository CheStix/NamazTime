from geopy.geocoders import Nominatim

from config import NOMINATIM_USER_AGENT

geo_locator = Nominatim(user_agent=NOMINATIM_USER_AGENT)


def get_loc_geocode(address: str, locator=geo_locator) -> list or None:
    """
    :param address:
    :param locator:
    :return: None если ничего не найдено
             False, если была ошибка во время запроса
             или список найденных местностей
    """
    try:
        find_locations = locator.geocode(address, exactly_one=False, limit=5)
    except:
        return False

    if find_locations is not None:
        locations = [loc for x in find_locations if (loc := x.raw)['class'] == 'place']
    else:
        return None

    return locations


if __name__ == '__main__':
    pass
    # locations = get_loc_geocode('Москва')
    # print(locations)

