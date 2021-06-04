from geopy.adapters import AioHTTPAdapter
from geopy.geocoders import GeoNames, TomTom

from config import GEONAMES_USERNAME, TOMTOM_API_KEY


async def format_location(location: dict) -> dict:
    """
    :param location: raw location dictionary
    :return: formatted dictionary with the display_name, lat and lon keys
    """
    entity_types = ['municipality', 'countryTertiarySubdivision',
                    'countrySecondarySubdivision', 'countrySubdivision', 'country']
    adr = location['address']
    names = []
    for entity in entity_types:
        if ((name := adr.get(entity)) is not None) and (name not in names):
            names.append(name)
    display_name = ', '.join(names)
    return {'display_name': display_name, 'lat': location['position']['lat'], 'lon': location['position']['lon']}


async def get_loc_geocode(address: str) -> dict:
    """
    :param address: The address or query you wish to geocode.
    :return: status:
                    'Error': error during search
                    None : nothing found
                    'Multiple': multiple search results
                    'Success': multiple search results
            display_name
            lat
            lon
    """
    response = {'status': None}
    async with TomTom(TOMTOM_API_KEY, adapter_factory=AioHTTPAdapter) as locator:
        try:
            find_locations = await locator.geocode(address, exactly_one=False, typeahead=True)
        except Exception as e:
            print(e)
            response['status'] = 'Error'
    if find_locations is not None:
        locations = [loc for x in find_locations if
                     (loc := x.raw)['type'] == 'Geography' and loc['entityType'] == 'Municipality']
        count = len(locations)
        if count == 1:
            response['status'] = 'Success'
            response.update(await format_location(locations[0]))
        elif count > 1:
            response['status'] = 'Multiple'
    return response


async def get_loc_timezone(lat: float, lon: float) -> int:
    """
    :param lat: Latitude. min/max: -90 to +90
    :param lon: Longitude. min/max: -180 to +180
    :return: time zone offset in hours
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
