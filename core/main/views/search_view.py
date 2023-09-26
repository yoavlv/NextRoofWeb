import pandas as pd
from django.core.paginator import Paginator
from django.shortcuts import redirect, render  # type: ignore # noqa: F401

from core.main.utils.search_utils import create_apartment_item

from ...NextRoofWeb.settings.dev import get_db_engine
from ..utils.search_utils import user_liked_id
from ..utils.sql_utils import cities_list_query, get_neighborhoods_for_city


def home(request):
    context = {}
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
    except Exception as e:
        user_logged_in = False
        liked_ids = []
        print(f"Error: {e}")  # It's good practice to log the actual error

    city_list = cities_list_query()

    if request.method != 'GET':
        return render(request, 'search.html', {
            'cities': city_list,
            'search': False,
            'user_logged_in': user_logged_in
        })

    params = {
        key: request.GET.get(key)
        for key in [
            'sort', 'city', 'neighborhood', 'street', 'min-rooms', 'max-rooms',
            'min-size', 'max-size', 'min-price', 'max-price', 'max-floor',
            'min-floor'
        ]
    }

    df_results = read_from_madlan_rank(params)

    # Apply sorting based on the sort parameter
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
    return render(
        request, 'search.html', {
            'apartments': page_obj,
            'num_results': num_results,
            'cities': city_list,
            'search': True,
            'user_search_params': params,
            'user_logged_in': user_logged_in
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
        'city': 'city',
        'neighborhood': 'neighborhood',
        'street': 'street',
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
    return df
