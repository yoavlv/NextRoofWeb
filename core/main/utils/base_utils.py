import difflib

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
