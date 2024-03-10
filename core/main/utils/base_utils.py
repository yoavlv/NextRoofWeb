import difflib
import math

from ..utils.plots import read_cities_and_streets_nadlan


def find_most_similar_word(word_list, target_word):
    target_word = target_word.decode('utf-8') if isinstance(
        target_word, bytes) else target_word
    matches = difflib.get_close_matches(target_word,
                                        word_list,
                                        n=1,
                                        cutoff=0.7)
    return matches[0] if matches else None


def get_key_by_value(dictionary, search_value):
    return next(
        (key for key, value in dictionary.items() if value == search_value),
        None)


def check_for_city_and_street_match(city_name, street_name=None):
    results = {
        'city_name': None,
        'city_id': None,
        'street_name': None,
        'street_id': None
    }
    city_dict = read_cities_and_streets_nadlan()

    search_city_name = find_most_similar_word(city_dict.values(), city_name)
    if search_city_name is None:
        return results

    city_id = get_key_by_value(city_dict, search_city_name)

    results['city_name'] = search_city_name
    results['city_id'] = city_id

    if not street_name:
        return results

    street_dict = read_cities_and_streets_nadlan(table_name='streets',
                                                 city_id=city_id)
    search_street_name = find_most_similar_word(street_dict.values(),
                                                street_name)
    if search_street_name is None:
        return results

    street_id = get_key_by_value(street_dict, search_street_name)

    results['street_name'] = search_street_name
    results['street_id'] = street_id

    return results


def wgs84_to_itm(lat, lon):
    # Constants for GRS80 Ellipsoid
    a = 6378137
    f = 1 / 298.257222101
    b = a * (1 - f)
    e_squared = (a**2 - b**2) / a**2

    # ITM Projection Parameters
    lat_origin = 31.7344
    lon_origin = 35.2074
    k0 = 1.0000067
    E0 = 219529.584
    N0 = 626907.39

    # Convert degrees to radians
    lat_rad = math.radians(lat)
    lon_rad = math.radians(lon)
    lat_origin_rad = math.radians(lat_origin)
    lon_origin_rad = math.radians(lon_origin)

    # Calculations
    e_prime_squared = e_squared / (1 - e_squared)
    N = a / math.sqrt(1 - e_squared * math.sin(lat_rad)**2)
    T = math.tan(lat_rad)**2
    C = e_prime_squared * math.cos(lat_rad)**2
    A = (lon_rad - lon_origin_rad) * math.cos(lat_rad)

    # Meridional Arc
    M = a * ((1 - e_squared / 4 - 3 * e_squared**2 / 64 - 5 * e_squared**3 / 256) * lat_rad -
             (3 * e_squared / 8 + 3 * e_squared**2 / 32 + 45 * e_squared**3 / 1024) * math.sin(2 * lat_rad) +
             (15 * e_squared**2 / 256 + 45 * e_squared**3 / 1024) * math.sin(4 * lat_rad) -
             (35 * e_squared**3 / 3072) * math.sin(6 * lat_rad))

    M0 = a * ((1 - e_squared / 4 - 3 * e_squared**2 / 64 - 5 * e_squared**3 / 256) * lat_origin_rad -
              (3 * e_squared / 8 + 3 * e_squared**2 / 32 + 45 * e_squared**3 / 1024) * math.sin(2 * lat_origin_rad) +
              (15 * e_squared**2 / 256 + 45 * e_squared**3 / 1024) * math.sin(4 * lat_origin_rad) -
              (35 * e_squared**3 / 3072) * math.sin(6 * lat_origin_rad))

    # ITM Easting and Northing
    ITM_Easting = E0 + k0 * N * (A + (1 - T + C) * A**3 / 6 + (5 - 18 * T + T**2 + 72 * C - 58 * e_prime_squared) * A**5 / 120)
    ITM_Northing = N0 + k0 * (M - M0 + N * math.tan(lat_rad) * (A**2 / 2 + (5 - T + 9 * C + 4 * C**2) * A**4 / 24 +
        (61 - 58 * T + T**2 + 600 * C - 330 * e_prime_squared) * A**6 / 720))

    return round(ITM_Easting, 3), round(ITM_Northing, 3)
