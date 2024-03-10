import datetime
import pickle
import re

import httpx
import numpy as np
import pandas as pd
from sqlalchemy import text

from ...NextRoofWeb.settings.dev import get_db_engine


def apt_data_complete(user_dict):
    year = datetime.datetime.now().year
    user_dict['year'] = year
    gush_helka = get_gush_helka_api(user_dict['city_id'],
                                    user_dict['street_id'],
                                    [user_dict['home_number']])
    if not gush_helka:
        return False

    user_dict['gush'] = gush_helka['gush']
    user_dict['helka'] = gush_helka['helka']

    rank_result = search_in_nadlan_clean(user_dict)
    user_dict['floors'] = rank_result['floors']
    user_dict['street_rank'] = rank_result['street_rank']
    user_dict['gush_rank'] = rank_result['gush_rank']
    user_dict['build_year'] = rank_result['build_year']
    user_dict['helka_rank'] = rank_result['helka_rank']
    user_dict['age'] = int(user_dict['year'] - user_dict['build_year'])

    return user_dict


def get_gush_helka_api(city_id, street_id, home_number):
    params = {
        'idCity': city_id,
        'streetCode': street_id,
        'HouseNo': home_number,
    }
    url = 'https://www.tabucheck.co.il/getGoshHelka.asp'

    try:
        response = httpx.get(url, params=params, timeout=10)
        response.raise_for_status()

        pattern = r'<strong>(.*?)</strong>'
        matches = re.findall(pattern, response.text)

        if len(matches) == 3:
            return {
                'gush': matches[1],
                'helka': matches[2],
            }

        else:
            print("Expected data not found in response.")
            return None
    except httpx.RequestError as e:
        print(f"An error occurred while requesting {e.request.url!r}.")
    except httpx.HTTPStatusError as e:
        print(
            f"Error response {e.response.status_code} while requesting {e.request.url!r}."
        )
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
    return None


def search_in_nadlan_clean(user_dict):
    engine = get_db_engine()
    city_id = int(user_dict['city_id'])
    street_id = int(user_dict['street_id'])
    gush = str(int(user_dict['gush']))
    helka = str(int(user_dict['helka']))
    home_number = str(int(user_dict['home_number']))
    year = int(user_dict['year'])  # Ensure year is an int for calculations
    results = {}

    with engine.connect() as conn:
        gush_rank_query = text(
            "SELECT gush_rank FROM nadlan_rank WHERE city_id = :city_id AND gush = :gush ORDER BY date DESC LIMIT 1"
        )

        helka_rank_query = text(
            "SELECT helka_rank, year FROM nadlan_rank WHERE gush = :gush AND helka = :helka ORDER BY date DESC LIMIT 1"
        )
        street_rank_query = text(
            "SELECT street_rank, year FROM nadlan_rank WHERE city_id = :city_id AND street_id = :street_id ORDER BY date DESC LIMIT 1"
        )
        build_year_query = text(
            "SELECT build_year, floors FROM nadlan_rank WHERE city_id = :city_id AND street_id = :street_id AND home_number = :home_number ORDER BY date DESC LIMIT 1"
        )

        gush_result = conn.execute(gush_rank_query, {
            'city_id': city_id,
            'gush': gush
        }).fetchone()
        if gush_result:
            results['gush_rank'] = gush_result[0]

        helka_result = conn.execute(helka_rank_query, {
            'gush': gush,
            'helka': helka
        }).fetchone()
        if helka_result:
            diff_year = helka_result[1] - year
            diff_year_floating = diff_year * 0.1
            helka_rank = helka_result[0] * (1 + diff_year_floating
                                            )  # Adjusted calculation
            results['helka_rank'] = helka_rank

        street_result = conn.execute(street_rank_query, {
            'city_id': city_id,
            'street_id': street_id
        }).fetchone()
        if street_result:
            diff_year = street_result[1] - year
            diff_year_floating = diff_year * 0.1
            street_rank = street_result[0] * (1 + diff_year_floating
                                              )  # Adjusted calculation
            results['street_rank'] = street_rank

        build_year_result = conn.execute(build_year_query, {
            'city_id': city_id,
            'street_id': street_id,
            'home_number': home_number
        }).fetchone()
        if build_year_result:
            results['build_year'], results['floors'] = build_year_result

    # Handle missing values for helka_rank, floors, and build_year
    if 'helka_rank' not in results or results['helka_rank'] is None:
        results['helka_rank'] = results.get('street_rank')

    if 'floors' not in results or results[
            'floors'] is None or 'build_year' not in results or results[
                'build_year'] is None:
        floor_avg, build_year_avg = read_from_nadlan_clean_calc_avg(
            city_id, street_id)
        if 'floors' not in results or results['floors'] is None:
            results['floors'] = floor_avg
        if 'build_year' not in results or results['build_year'] is None:
            results['build_year'] = int(build_year_avg)

    return results


def read_from_nadlan_clean_calc_avg(city_id, street_id):
    engine = get_db_engine()
    with engine.connect() as conn:
        query = "SELECT floors, build_year FROM nadlan_rank WHERE city_id = %s AND street_id = %s"
        df = pd.read_sql_query(query, conn, params=(
            city_id,
            street_id,
        ))
    df.replace({'NaN': np.nan, 'None': np.nan}, inplace=True)
    df = df.dropna(subset=['floors', 'build_year'])
    df.loc[:, 'floors'] = df['floors'].astype(float).astype(np.int32)
    df.loc[:, 'build_year'] = df['build_year'].astype(float).astype(np.int32)
    floors_avg = df['floors'].mean()
    build_year_avg = df['build_year'].mean()
    return floors_avg, build_year_avg


def read_model_scaler_from_db(city_id, model=False, scaler=False):
    engine = get_db_engine()
    with engine.connect() as conn:
        if model:
            query = text(
                "SELECT model_data FROM ml_models WHERE city_id = :city_id AND model_name = 'stacking'"
            )
        if scaler:
            query = text(
                "SELECT model_scaler FROM ml_models WHERE city_id = :city_id AND model_name = 'stacking'"
            )
        data = conn.execute(query, {'city_id': city_id}).fetchone()[0]
        return pickle.loads(data)
