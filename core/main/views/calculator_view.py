import datetime
from django.http import HttpResponse  # noqa: F401
from django.shortcuts import render
from sklearn.preprocessing import MinMaxScaler  # noqa: F401
from core.main.utils.plots import *
from ..utils.base_utils import find_most_similar_word, get_key_by_value
from ..utils.plots import read_cities_and_streets_nadlan
from ..utils.sql_utils import save_user_search
from ..utils.utils_api import apt_data_complete, read_model_scaler_from_db


def get_asset_type(params):
    expected_cols = [
        'type_apartment', 'type_apartment_in_building',
        'type_rooftop_apartment', 'type_penthouse', 'type_garden_apartment'
    ]
    for col in expected_cols:
        params[col] = 0

    if params['asset_type'] == 1:
        params['type_apartment_in_building'] = 1

    elif params['asset_type'] == 2:
        params['type_garden_apartment'] = 1

    elif params['asset_type'] == 3:
        params['type_rooftop_apartment'] = 1
    else:
        params['type_rooftop_apartment'] = 1

    return params


def asset_value_view(request):
    search = False
    predicted_price = None
    city_plt = None
    street_plt = None
    last_deals = None
    params = {}

    # Handle the GET request
    if request.method == 'GET' and request.GET:
        search = True
        params['city'] = str(request.GET.get('city')).strip()
        params['street'] = str(request.GET.get('street')).strip()
        params['home_number'] = int(request.GET.get('home-number'))
        params['rooms'] = int(request.GET.get('rooms'))
        params['size'] = int(request.GET.get('size'))
        params['floor'] = int(request.GET.get('floor'))
        params['new'] = int(request.GET.get('condition'))
        params['year'] = int(datetime.datetime.now().year)
        params['parking'] = int(request.GET.get('parking'))
        params['asset_type'] = int(request.GET.get('asset_type'))

        params = get_asset_type(params)

        city_dict = read_cities_and_streets_nadlan(table_name='nadlan_clean')
        search_city_name = find_most_similar_word(city_dict.values(),
                                                  params['city'])

        if not search_city_name:
            error_message = f"לא מצאנו תוצאות עבור: {params['city']}"
            return render(
                request, "asset_value.html", {
                    'error_message': error_message,
                    'params': params,
                    'search': False,
                })

        params['city'] = search_city_name
        city_id = get_key_by_value(city_dict, search_city_name)
        params['city_id'] = city_id

        street_dict = read_cities_and_streets_nadlan(table_name='nadlan_clean',
                                                     city_id=city_id)
        search_street_name = find_most_similar_word(street_dict.values(),
                                                    params['street'])

        if not search_street_name:
            error_message = f"לא מצאנו תוצאות עבור: {params['street']}"
            return render(
                request, "asset_value.html", {
                    'error_message': error_message,
                    'params': params,
                    'search': False,
                })

        params['street'] = search_street_name
        street_id = get_key_by_value(street_dict, search_street_name)
        params['street_id'] = street_id
        apt_params = apt_data_complete(params)
        save_user_search(request, params['city'], params['city_id'],
                         params['street_id'], params['street'], str(params))

        if not apt_params:
            addr = f"{params['city']}, {params['street'], params['home_number']}"
            error_message = f"לא מצאנו תוצאות עבור: {addr}"
            return render(
                request, "asset_value.html", {
                    'error_message': error_message,
                    'params': params,
                    'search': False,
                })

        else:
            model = read_model_scaler_from_db(city_id, model=True)
            predicted_price = predict_apt_price(apt_params, model)

            if params['parking'] == 1:
                predicted_price = predicted_price * 1.05
            elif params['parking'] == 2:
                predicted_price = predicted_price * 1.07
            elif params['parking'] == 3:
                predicted_price = predicted_price * 1.08

            predicted_price = round_last_three_digits(int(predicted_price))
            predicted_price = "₪{:,}".format(int(predicted_price))
            street_plt = street_plot(params['city_id'], params['city'],
                                     params['street_id'], params['street'])

            city_plt = city_plot(params['city_id'], params['city'])
            last_deals = lasted_deals_street(params['city_id'], params['city'],
                                             params['street_id'],
                                             params['street'])

    return render(
        request, "asset_value.html", {
            'predicted_price': predicted_price,
            'params': params,
            'search': search,
            'street_plt': street_plt,
            'city_plt': city_plt,
            'last_deals': last_deals,
        })


def predict_apt_price(params, model):
    df = pd.DataFrame([params])
    df['type_apartment'] = 0
    cols = [
        "rooms", "floor", "size", "build_year", "floors", "year", "age",
        "gush_rank", "street_rank", "helka_rank", "new", 'type_apartment',
        'type_apartment_in_building', 'type_rooftop_apartment',
        'type_penthouse', 'type_garden_apartment'
    ]
    df = df.reindex(columns=cols)
    scaler = read_model_scaler_from_db(params['city_id'], scaler=True)
    X_scaled = scaler.transform(df)
    y_pred = model.predict(X_scaled)
    appraised_price = int(y_pred[0])
    return appraised_price


def round_last_three_digits(number):
    last_three_digits = number % 1000
    rounded_last_three_digits = round(last_three_digits, -3)
    rounded_number = number - last_three_digits + rounded_last_three_digits
    return rounded_number
