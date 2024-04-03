import json
import pandas as pd
from django.core.paginator import Paginator
from django.shortcuts import redirect, render  # type: ignore # noqa: F401
from core.main.utils.search_utils import create_apartment_item
from ...NextRoofWeb.settings.dev import get_db_engine
from ..utils.base_utils import check_for_city_and_street_match
from ..utils.search_utils import user_liked_id
from ..utils.sql_utils import save_user_search
from .map_view import fetch_and_process_polygons


def home(request):
    selected_year = request.GET.get(
        'year', 2023)  # Default to 2023 if no year is specified
    selected_year = int(selected_year)
    years = [i for i in range(2010, 2025)]
    polygons_list, max_rank, min_rank = fetch_and_process_polygons(
        selected_year)
    context = {
        'selected_year': selected_year,
        'years': years,
        'polygons':
        json.dumps(polygons_list
                   ),  # Ensure polygons are JSON serialized for JavaScript use
        'max_rank': max_rank,
        'min_rank': min_rank,
    }
    top_deals = get_random_deals()
    context['top_deals'] = top_deals
    return render(request, "home.html", context)


def login(request):
    return render(request, "login.html")


def get_random_deals(num_deals=3):
    engine = get_db_engine()
    query = """
        SELECT r.street, r.item_id, r.rooms, r.neighborhood, r.floor, r.size, r.city, r.price,
               p.predicted, r.images, p.difference
        FROM madlan_rank r
        JOIN madlan_predict p ON p.item_id = r.item_id
        WHERE r.price < p.predicted
        ORDER BY RANDOM()
        LIMIT %s;
    """
    df = pd.read_sql_query(query, engine, params=(num_deals, ))

    # Transform each row in DataFrame to an apartment item
    apartments = [create_apartment_item(row) for index, row in df.iterrows()]
    return apartments


def search_apartments(request):

    try:
        user_logged_in = request.is_user_logged_in
        liked_ids = user_liked_id(request.user_id) if user_logged_in else []
    except Exception:
        user_logged_in = False
        liked_ids = []

    context = {
        'search': True,
        'user_logged_in': user_logged_in,
        'error_message': ''
    }

    city = request.GET.get('city', None)
    street = request.GET.get('street', None)
    if not city:  # No city in search query
        context.update({
            'search': False,
        })

        return render(request, 'search.html', context)
    params = {
        key: request.GET.get(key, None)
        if request.GET.get(key, None) != '' else None
        for key in [
            'sort', 'city', 'neighborhood', 'street', 'min-rooms', 'max-rooms',
            'min-size', 'max-size', 'min-price', 'max-price', 'max-floor',
            'min-floor'
        ]
    }

    results = check_for_city_and_street_match(params['city'], params['street'])

    params['city_id'] = results.get('city_id')
    params['street_id'] = results.get('street_id')
    save_user_search(request, city, params['city_id'], params['street_id'],
                     street, str(params))

    if not params['city_id']:
        context.update({
            'search':
            True,
            'error_message':
            f"לא נמצאו תוצאות עבור העיר {params['city']}"
        })
        return render(request, 'search.html', context)

    # Street specified but not found, and city found
    if street and not params['street_id']:
        context.update({
            'search':
            True,
            'error_message':
            f"הרחוב {street} לא נמצא בעיר {params['city']}"
        })
        return render(request, 'search.html', context)

    df_results = read_from_madlan_rank(params)

    sort_option = params.get('sort')
    if sort_option == 'price_asc':
        df_results.sort_values(by='price', ascending=True, inplace=True)
    elif sort_option == 'price_desc':
        df_results.sort_values(by='price', ascending=False, inplace=True)

    # Create apartment items with liked status
    apartments = [
        create_apartment_item(res, liked=str(res[1]) in liked_ids)
        for index, res in df_results.iterrows()
    ]

    paginator = Paginator(apartments, 12)  # Show 12 apartments per page
    page_obj = paginator.get_page(request.GET.get('page'))
    num_results = len(apartments)

    params['city'] = results['city_name'] or ''
    params['street'] = results['street_name'] or ''
    return render(
        request, 'search.html', {
            'apartments': page_obj,
            'num_results': num_results,
            'search': True,
            'user_search_params': params,
            'user_logged_in': user_logged_in,
        })


def read_from_madlan_rank(params):
    engine = get_db_engine()
    query = """
    SELECT r.street, r.item_id, r.rooms, r.neighborhood, r.floor, r.size, r.city, r.price,
           p.predicted, r.images as madlan_predicted, p.difference
    FROM madlan_rank r
    JOIN madlan_predict p ON p.item_id = r.item_id
    WHERE
    """
    conditions = []
    query_params = []

    # Map the parameter names to the database column names
    param_to_db_column = {
        'city_id': 'city_id',
        'street_id': 'street_id',
        'min-rooms': 'rooms',
        'max-rooms': 'rooms',
        'min-size': 'size',
        'max-size': 'size',
        'min-price': 'price',
        'max-price': 'price',
        'max-floor': 'floor',
        'min-floor': 'floor'
    }

    for param, db_column in param_to_db_column.items():
        value = params.get(param)
        if value not in [None, '']:
            if param in [
                    'min-rooms', 'max-rooms', 'min-size', 'max-size',
                    'min-price', 'max-price', 'max-floor', 'min-floor'
            ]:
                try:
                    value = int(value)
                except ValueError:
                    continue

            if param.startswith('min-'):
                operator = '>='
            elif param.startswith('max-'):
                operator = '<='
            else:  # Handle exact matches
                operator = '='

            conditions.append(f"r.{db_column} {operator} %s")
            query_params.append(value)

    query += ' AND '.join(
        conditions
    ) if conditions else '1=1'  # '1=1' is used to handle no conditions

    df = pd.read_sql_query(query, engine, params=tuple(query_params))
    df = df.replace([None, 'NaN', 'None'], '')
    return df
