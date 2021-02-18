from geopy.geocoders import Nominatim


def get_location(address: str):
    # Поиск местности по адресу, возвращаем список найденного или None если ничего не найдено или False при ошибке
    geolocator = Nominatim(user_agent="NamazTime_TGBot")
    try:
        find_locations = geolocator.geocode(address, exactly_one=False, limit=5)
    except:
        find_locations = False

    if not find_locations:
        return find_locations

    locations = []
    for loc in find_locations:
        loc = loc.raw
        if loc['class'] == 'place':
            locations.append(loc)
    return locations


if __name__ == '__main__':
    locations = get_location('Самара')
    print(locations)

