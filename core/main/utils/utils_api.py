import datetime
import pickle
from sqlalchemy import text
from ...NextRoofWeb.settings.dev import get_db_engine

def apt_data_complete(user_dict):
    year = datetime.datetime.now().year
    user_dict['year'] = year

    results = find_location_data(user_dict['city_id'], user_dict['street_id'],user_dict['home_number'])
    if not results:
        return False
    user_dict['gush'] = results[0]
    user_dict['helka'] = results[1]

    rank_result = search_in_nadlan_clean(user_dict)
    user_dict['floors'] = rank_result['floors']
    user_dict['street_rank'] = rank_result['street_rank']
    user_dict['gush_rank'] = rank_result['gush_rank']
    user_dict['build_year'] = rank_result['build_year']
    user_dict['helka_rank'] = rank_result['helka_rank']
    user_dict['age'] = int(user_dict['year'] - user_dict['build_year'])
    return user_dict


def search_in_nadlan_clean(user_dict):
    engine = get_db_engine()
    city_id = int(user_dict['city_id'])
    street_id = int(user_dict['street_id'])
    gush = str(int(user_dict['gush']))
    helka = str(int(user_dict['helka']))
    home_number = str(int(user_dict['home_number']))
    results = {}

    with engine.connect() as conn:

        gush_rank_query = text(
            "SELECT gush_rank FROM gush_rank_table WHERE gush = :gush"
        )
        helka_rank_query = text(
            "SELECT helka_rank, year FROM helka_rank_table WHERE gush = :gush AND helka = :helka"
        )
        street_rank_query = text(
            "SELECT street_rank FROM street_rank_table WHERE city_id = :city_id AND street_id = :street_id"
        )
        build_year_query = text(
            "SELECT max_build_year FROM build_year_view WHERE city_id = :city_id AND street_id = :street_id AND home_number = :home_number"
        )
        floors_query = text(
            "SELECT max_floors FROM floors_view WHERE city_id = :city_id AND street_id = :street_id AND home_number = :home_number"
        )

        gush_result = conn.execute(gush_rank_query, {
            'gush': gush
        }).fetchone()

        if gush_result:
            results['gush_rank'] = gush_result[0]

        helka_result = conn.execute(helka_rank_query, {
            'gush': gush,
            'helka': helka
        }).fetchone()

        if helka_result:
            results['helka_rank'] = helka_result[0]

        street_result = conn.execute(street_rank_query, {
            'city_id': city_id,
            'street_id': street_id
        }).fetchone()
        if street_result:
            results['street_rank'] = street_result[0]

        build_year_result = conn.execute(build_year_query, {
            'city_id': city_id,
            'street_id': street_id,
            'home_number': home_number
        }).fetchone()
        if build_year_result:
            results['build_year'] = build_year_result[0]

        floors_result = conn.execute(floors_query, {
            'city_id': city_id,
            'street_id': street_id,
            'home_number': home_number
        }).fetchone()

        if floors_result:
            results['floors'] = floors_result[0]

        if 'floors' not in results or 'build_year' not in results:
            floors_avg, build_year_avg = read_from_nadlan_clean_calc_avg(city_id, street_id)

            if 'floors' not in results and floors_avg is not None:
                results['floors'] = floors_avg

            if 'build_year' not in results and build_year_avg is not None:
                results['build_year'] = build_year_avg

    return results

def read_from_nadlan_clean_calc_avg(city_id, street_id):
    engine = get_db_engine()
    with engine.connect() as conn:
        query = text("SELECT avg_floors, avg_build_year FROM floors_and_build_year_avg_view WHERE city_id = :city_id AND street_id = :street_id")
        result = conn.execute(query, {'city_id': city_id, 'street_id': street_id}).fetchone()
        return result if result else (None, None)


def read_model_scaler_from_db(city_id, model=False, scaler=False):
    engine = get_db_engine()
    with engine.connect() as conn:
        select_clause = "model_data" if model else "model_scaler" if scaler else None
        if select_clause:
            query = text(f"SELECT {select_clause} FROM ml_models WHERE city_id = :city_id AND model_name = 'stacking'")
            data = conn.execute(query, {'city_id': city_id}).fetchone()[0]
            return pickle.loads(data)
        return None

def find_location_data(city_id, street_id, home_number):
    engine = get_db_engine()
    with engine.connect() as conn:
        query = text(
            "SELECT gush, helka FROM gush_helka WHERE city_id = :city_id AND street_id = :street_id AND home_number = :home_number"
        )
        result = conn.execute(query, {
            'city_id': city_id,
            'street_id': street_id,
            'home_number': home_number,
        }).fetchone()

    if result:
        gush, helka = result
        return gush, helka
    else:
        return False
