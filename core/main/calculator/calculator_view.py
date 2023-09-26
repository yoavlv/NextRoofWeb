import datetime

import joblib
from django.http import HttpResponse  # noqa: F401
from django.shortcuts import render
from sklearn.preprocessing import MinMaxScaler  # noqa: F401

# from core.main.views.base_functions import lasted_deals_street  # noqa: E402
from core.main.utils.plots import *

from ..utils.calc_utils import city_dict
from ..utils.sql_utils import cities_list_query
from .api import apt_data_complete


def asset_value_page(request):
    Search = False
    city_list = cities_list_query(table_name='nadlan_rank')

    return render(request, "asset_value.html", {
        'cities': city_list,
        'Search': Search
    })


def calc_asset_value(request):
    city_list = cities_list_query(table_name='nadlan_rank')
    if request.method != 'GET':
        Search = False
        return render(request, "asset_value.html", {
            'cities': city_list,
            'Search': Search,
        })

    params = {}
    Search = False
    if request.method == 'GET':
        Search = True
        params['city'] = str(request.GET.get('city')).strip()
        params['street'] = str(request.GET.get('street')).strip()
        params['home_number'] = int(request.GET.get('home-number'))
        params['rooms'] = int(request.GET.get('rooms'))
        params['size'] = int(request.GET.get('size'))
        params['floor'] = int(request.GET.get('floor'))
        params['new'] = int(request.GET.get('condition'))
        params['year'] = int(datetime.datetime.now().year)

        apt_params = apt_data_complete(params)
        if not apt_params:

            addr = f"{params['city']}, {params['street'], params['home_number']}"

            error_message = f"לא מצאנו תוצאות עבור: {addr}"
            print(error_message)
            return render(
                request, "asset_value.html", {
                    'error_message': error_message,
                    'cities': city_list,
                    'Search': False,
                })
        city = str(apt_params['city']).strip()

        models = joblib.load(
            f'core/static/models/{city_dict[city]}_saved_models.pkl')
        model = models['stacking']

        predicted_price = predict_apt_price(apt_params, model)
        predicted_price = "₪{:,}".format(predicted_price)

        neighborhood_plt = neighborhood_plot(params['city'],
                                             params['neighborhood'])
        city_plt = city_plot(params['city'])
        last_deals = lasted_deals_street(params['city'], params['street'])
        return render(
            request, "asset_value.html", {
                'predicted_price': predicted_price,
                'params': params,
                'Search': Search,
                'neighborhood_plt': neighborhood_plt,
                'city_plt': city_plt,
                'last_deals': last_deals,
                'cities': city_list,
            })

    return render(request, "asset_value.html", {
        'cities': city_list,
        'Search': Search
    })


def predict_apt_price(params, model):
    df = pd.DataFrame([params])
    df = df.reindex(columns=[
        "rooms", "floor", "size", "build_year", "floors", "year", "age",
        "neighborhood_rank", "street_rank", "helka_rank", "new"
    ])
    city_code = city_dict[params['city']]
    scaler = joblib.load(f"core/static/models/{city_code}_scaler.pkl")

    X_scaled = scaler.transform(df)
    y_pred = model.predict(X_scaled)
    appraised_price = int(y_pred[0])
    return appraised_price
