import datetime

import joblib
from django.http import HttpResponse  # noqa: F401
from django.shortcuts import render
from sklearn.preprocessing import MinMaxScaler  # noqa: F401

# from core.main.views.base_functions import lasted_deals_street  # noqa: E402
from core.main.utils.plots import *

from ..utils.calc_utils import city_dict
from ..utils.sql_utils import cities_list_query
from .api import apt_data_complete, read_model_scaler_from_db


def asset_value_view(request):
    city_list = cities_list_query(table_name='nadlan_rank')
    search = False
    predicted_price = None
    neighborhood_plt = None
    city_plt = None
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

        apt_params = apt_data_complete(params)
        if not apt_params:
            addr = f"{params['city']}, {params['street'], params['home_number']}"
            error_message = f"לא מצאנו תוצאות עבור: {addr}"
            return render(
                request, "asset_value.html", {
                    'error_message': error_message,
                    'params': params,
                    'search': False,
                    'cities': city_list,
                })

        else:
            city = str(apt_params['city']).strip()
            # Uncomment and modify this line as necessary to load your model
            # model = joblib.load(f'core/static/models/{city_dict[city]}_saved_models.pkl')['stacking']
            model = read_model_scaler_from_db(city_dict[city], model=True)

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
            'search': search,
            'neighborhood_plt': neighborhood_plt,
            'city_plt': city_plt,
            'last_deals': last_deals,
            'cities': city_list,
        })


def predict_apt_price(params, model):
    df = pd.DataFrame([params])
    df = df.reindex(columns=[
        "rooms", "floor", "size", "build_year", "floors", "year", "age",
        "neighborhood_rank", "street_rank", "helka_rank", "new"
    ])
    city_code = city_dict[params['city']]
    # scaler = joblib.load(f"core/static/models/{city_code}_scaler.pkl")
    scaler = read_model_scaler_from_db(city_code, scaler=True)
    X_scaled = scaler.transform(df)
    y_pred = model.predict(X_scaled)
    appraised_price = int(y_pred[0])
    return appraised_price
