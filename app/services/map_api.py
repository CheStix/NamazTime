from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import Nominatim, GeoNames

from config import NOMINATIM_USER_AGENT, GEONAMES_USERNAME


async def get_loc_geocode(address: str) -> list or None:
    """
    :param address:
    :return: None если ничего не найдено
             False, если была ошибка во время запроса
             или список найденных местностей
    """
    async with Nominatim(user_agent=NOMINATIM_USER_AGENT, adapter_factory=AioHTTPAdapter) as locator:
        try:
            find_locations = await locator.geocode(address, exactly_one=False, limit=5, featuretype='settlement')
        except Exception as e:
            print(e)
            return False
    if find_locations is not None:
        locations = [loc for x in find_locations if (loc := x.raw)['class'] == 'place']
    else:
        return None
    return locations


async def get_loc_timezone(lat: float, lon: float) -> int:
    """

    :param lat:
    :param lon:
    :return:
    """
    async with GeoNames(GEONAMES_USERNAME, adapter_factory=AioHTTPAdapter) as locator:
        try:
            timezone = await locator.reverse_timezone((lat, lon))
        except Exception as e:
            print(e)
            return False
        finally:
            return timezone.raw['rawOffset']


if __name__ == '__main__':
    pass
    # t = asyncio.run(get_loc_timezone(45.401805, -75.699828))
    # print(t)
    # locations = get_loc_geocode('Москва')
    # print(locations)
