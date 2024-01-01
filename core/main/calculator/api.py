import datetime
import pickle
import re

import httpx
import numpy as np
import pandas as pd
from sqlalchemy import text

from ...NextRoofWeb.settings.dev import get_db_engine


def apt_data_complete(user_dict):
    addr = user_dict['city'] + ' ' + user_dict['street'] + ' ' + str(
        user_dict['home_number'])

    gush_helka = get_gush_helka_api(addr)
    if not gush_helka:
        return False

    user_dict['gush'] = gush_helka['gush']
    user_dict['helka'] = gush_helka['helka']

    rank_result = search_in_nadlan_clean(user_dict)

    govmap_result = govmap_addr(addr)

    if govmap_result['success']:
        user_dict['x'] = govmap_result['x']
        user_dict['y'] = govmap_result['y']

    nominatim_result = nominatim_addr(addr)
    if nominatim_result['success']:
        user_dict['lat'] = nominatim_result['lat']
        user_dict['long'] = nominatim_result['long']

    user_dict['neighborhood'] = rank_result['neighborhood']
    user_dict['helka_rank'] = rank_result['helka_rank']
    user_dict['street_rank'] = rank_result['street_rank']
    user_dict['neighborhood_rank'] = rank_result['neighborhood_rank']
    user_dict['build_year'] = rank_result['build_year']
    user_dict['floors'] = rank_result['floors']

    user_dict['year'] = int(datetime.datetime.now().year)
    user_dict['age'] = int(user_dict['year'] - user_dict['build_year'])
    return user_dict


def get_gush_helka_api(addr):
    address = addr.strip()
    json_data = {
        'whereValues': [address],
        'locateType': 2,
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.post(
                'https://ags.govmap.gov.il/Search/ParcelLocate',
                json=json_data)
            response.raise_for_status(
            )  # This will raise an exception for HTTP error responses

            json_obj = response.json()
            # Check for errors in the response data
            if json_obj.get('errorCode') == 0 and json_obj.get('status') == 0:
                try:
                    gush = int(json_obj['data']['ResultData']['Values'][0]
                               ['Values'][0])
                    helka = int(json_obj['data']['ResultData']['Values'][0]
                                ['Values'][1])
                    return {'gush': gush, 'helka': helka}
                except (IndexError, ValueError, KeyError):
                    # Handle exceptions related to data extraction
                    print("Error extracting 'gush' and 'helka' from response.")
                    return False

    except httpx.HTTPStatusError as e:
        print(f"HTTP error occurred: {e}")
    except Exception as e:
        print(f"An error occurred: {e}")
    return False


def split_address(address):
    try:
        match = re.match(
            r'([\u0590-\u05FF\'"׳״\-\s]+)\s(\d+).*?,\s*([\u0590-\u05FF\s-]+)',
            address)
        if not match:
            raise ValueError(f"Invalid address format: {address}")

        street, home_number, city = match.groups()
        return {
            'street': street.strip(),
            'home_number': home_number,
            'city': city.strip()
        }
    except Exception as e:
        raise Exception(f"Error parsing address: {e}")


def govmap_addr(addr):
    link = f"https://es.govmap.gov.il/TldSearch/api/DetailsByQuery?query={addr}&lyrs=276267023&gid=govmap"
    result = {}

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(link)
            if response.status_code == 200:
                json_obj = response.json()
                if json_obj['Error'] == 0:
                    try:
                        address = split_address(
                            json_obj['data']['ADDRESS'][0]['ResultLable'])
                        result = {
                            'city': address['city'],
                            'street': address['street'],
                            'y': json_obj['data']['ADDRESS'][0]['Y'],
                            'x': json_obj['data']['ADDRESS'][0]['X'],
                            'success': True,
                        }
                        return result
                    except:
                        neighborhood_obj = json_obj['data']['NEIGHBORHOOD'][0][
                            'ResultLable']
                        neighborhood = neighborhood_obj.split(',')
                        result = {
                            'city': (neighborhood[1]).strip(),
                            'neighborhood': (neighborhood[0]).strip()
                        }
                        return result

        return {'success': False}
    except httpx.RequestError as e:
        print(f"An error occurred with GovMap API: {e}")
        return {'success': False}


def nominatim_addr(query):
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {'q': query, 'format': 'jsonv2', 'addressdetails': 1}
    result = {
        "neighborhood": None,
        "type": None,
        "zip": None,
        "lat": None,
        "long": None,
        'success': False,
    }

    try:
        with httpx.Client(timeout=30) as client:
            response = client.get(base_url, params=params)
            if response.status_code == 200:
                data = response.json()
                if data:
                    address = data[0].get('address', {})
                    result = {
                        "city":
                        address.get("city", ""),
                        "neighborhood":
                        address.get("suburb")
                        or address.get("neighborhood", ""),
                        "street":
                        address.get("road", ""),
                        "zip":
                        address.get("postcode", ""),
                        "type":
                        data[0].get("type", ""),
                        "lat":
                        round(float(data[0].get("lat", "0")), 5),
                        "long":
                        round(float(data[0].get("lon", "0")), 5),
                        'success':
                        True,
                    }
                    return result
        return result
    except httpx.RequestError as e:
        print(f"Failed to connect to the Nominatim API: {e}")
        return result


def search_in_nadlan_clean(user_dict):
    engine = get_db_engine()
    city = user_dict['city'].strip()
    street = user_dict['street'].strip()
    gush = str(int(user_dict['gush']))
    helka = str(int(user_dict['helka']))
    home_number = str(int(user_dict['home_number']))

    with engine.connect() as connection:
        query_neighborhood = text(
            "SELECT neighborhood, street_rank, neighborhood_rank FROM nadlan_rank WHERE city = :city AND street = :street ORDER BY date DESC LIMIT 1"
        )
        neighborhood_result = connection.execute(query_neighborhood, {
            'city': city,
            'street': street
        }).fetchone()

        if neighborhood_result:
            neighborhood, street_rank, neighborhood_rank = neighborhood_result
        else:
            return False

        query_2 = text(
            "SELECT helka_rank FROM nadlan_rank WHERE gush = :gush and helka = :helka order by date desc LIMIT 1"
        )
        helka_rank_result = connection.execute(query_2, {
            'gush': gush,
            'helka': helka
        }).fetchone()

        query_3 = text(
            "SELECT floors, build_year FROM nadlan_rank WHERE city = :city and neighborhood = :neighborhood and street = :street and home_number = :home_number order by date desc LIMIT 1"
        )
        build_year_floors_result = connection.execute(
            query_3, {
                'street': street,
                'neighborhood': neighborhood,
                'home_number': home_number,
                'city': city
            }).fetchone()

        # Compile results
        results = {
            'neighborhood':
            neighborhood,
            'street_rank':
            street_rank,
            'neighborhood_rank':
            neighborhood_rank,
            'helka_rank':
            helka_rank_result[0] if helka_rank_result else None,
            'floors':
            build_year_floors_result[0] if build_year_floors_result else None,
            'build_year':
            build_year_floors_result[1] if build_year_floors_result else None,
        }

    if results['helka_rank'] is None:
        results['helka_rank'] = results['street_rank']

    if results['floors'] is None or results['build_year'] is None:
        floor_avg, build_year_avg = read_from_nadlan_clean_calc_avg(
            city, street)

    if results['floors'] is None:
        results['floors'] = floor_avg

    if results['build_year'] is None:
        print('avg')
        results['build_year'] = int(build_year_avg)

    return results


def read_from_nadlan_clean_calc_avg(city, street):
    engine = get_db_engine()
    query = "SELECT floors, build_year FROM nadlan_rank WHERE city = %s AND street = %s"
    df = pd.read_sql_query(query, engine, params=(
        city,
        street,
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
                "SELECT model_data FROM ml_models WHERE city_code = :city_id AND model_name = 'stacking'"
            )
        if scaler:
            query = text(
                "SELECT model_scaler FROM ml_models WHERE city_code = :city_id AND model_name = 'stacking'"
            )
        data = conn.execute(query, {'city_id': city_id}).fetchone()[0]
        return pickle.loads(data)
