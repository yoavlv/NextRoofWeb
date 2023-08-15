import matplotlib
from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
import pandas as pd
import csv
import numpy as np
from datetime import datetime
import math
import joblib
from sklearn.preprocessing import MinMaxScaler
from catboost import CatBoostRegressor
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import StackingRegressor, RandomForestRegressor, GradientBoostingRegressor
from xgboost import XGBRegressor
import lightgbm as lgb
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from django.http import JsonResponse
import io
import base64
from .base_functions import lasted_deals_street

def asset_value_page(request):

    df_history_deals = pd.read_csv('data/Nadlan_clean.csv')
    neighborhoods = sorted(df_history_deals['Neighborhood'].unique())
    streets = list(sorted(df_history_deals['Street'].unique()))
    Search = False

    return render(request, "asset_value.html",{'neighborhoods': neighborhoods , 'Search':Search ,'streets':streets})


def calc_asset_value(request):

    df_history_deals = pd.read_csv('data/Nadlan_clean.csv')
    neighborhoods = sorted(set(df_history_deals['Neighborhood']))
    streets = sorted(set(df_history_deals['Street']))
    params = {}
    Search = False
    if request.method == 'GET':
        Search = True
        params['City'] = str(request.GET.get('city')).strip()
        params['Neighborhood'] = str(request.GET.get('neighborhood')).strip()
        params['Street'] = str(request.GET.get('street')).strip()
        params['Home_number'] = int(request.GET.get('home-number'))
        params['Rooms'] = int(request.GET.get('rooms'))
        params['Size'] = int(request.GET.get('size'))
        params['Floor'] = int(request.GET.get('floor'))
        params['Year'] = 2023
        # df = db_to_df('address')
        df = pd.read_csv("static/Address.csv")
        params = calc_missing_values(df, params)
        models = joblib.load('static/saved_models.pkl')
        model = models['stacking']

        predicted_price = predict_apt_price(params,model)
        predicted_price = "₪{:,}".format(predicted_price)
        df = pd.read_csv('data/Nadlan_clean.csv')
        neighborhood_plt = Price_Increases_Neighborhood(df,params['Neighborhood'])
        last_deals = lasted_deals_street( params['Street'])
        return render(request, "asset_value.html", {'predicted_price':predicted_price,'neighborhoods':neighborhoods ,
                                                    'streets':streets ,'params':params, 'Search':Search ,'neighborhood_plt':neighborhood_plt,
                                                    'last_deals':last_deals})

    return render(request, "asset_value.html",{'neighborhoods': neighborhoods,'Search':Search})
def calc_distance_from_the_see_TLV(X_coordinate, Y_coordinate):
    north_x = 180471
    north_y = 672391
    south_x = 177333
    south_y = 663016

    m = (south_y - north_y) / (south_x - north_x)
    b = north_y - (m * north_x)

    numerator = abs(m * X_coordinate - Y_coordinate + b)
    denominator = math.sqrt(m ** 2 + 1)
    return numerator / denominator


def calc_distance_from_train_station(x, y):
    stations = [(179820.47, 662424.54), (180619, 664469.56), (181101.44, 665688.78), (181710.96, 667877.05)]
    distances = [abs(station[0] - x) + abs(station[1] - y) for station in stations]
    min_distance = min(distances)
    return min_distance


def add_neighborhood(search_street):
    df = pd.read_csv("data/Nadlan_clean.csv")
    neighborhoods = {}
    for index, row in df.iterrows():
        neighborhood = row['Neighborhood']
        street = row['Street']
        if neighborhood not in neighborhoods:
            neighborhoods[neighborhood] = set()
        neighborhoods[neighborhood].add(street)

    for neighborhood, streets in neighborhoods.items():
        if search_street in streets:
            return neighborhood

    return None




def check_for_match(df, params, number, target, col_1, col_2=None):
    number = int(number)
    number_offsets = [number, number - 1, number + 1, number + 2, number - 2, number + 3, number - 3, number + 4,
                      number - 4, number + 5, number - 5]
    for number in number_offsets:
        if col_2:
            try:
                match = df.loc[(df[col_1] == params[col_1]) & (df[col_2] == number), target].values[0]
                return match
            except:
                pass
        else:
            try:
                match = df.loc[(df[col_1] == params[col_1]), target].values[0]
                return match
            except:
                pass
    # print("Mean")
    # print(target)
    return int(df[target].mean())


def calc_missing_values(df, params):

    params['Lat'] = check_for_match(df, params, params['Home_number'], 'y', 'Street', 'Home_number')
    params['Long'] = check_for_match(df, params , params['Home_number'] , 'x' , 'Street' ,'Home_number')

    params['Gush'] = check_for_match(df, params, params['Home_number'], 'Gush', 'Street', 'Home_number')
    params['Helka'] = check_for_match(df, params, params['Home_number'], 'Helka', 'Street', 'Home_number')

    params['Distance_sea'] = calc_distance_from_the_see_TLV(params['Long'], params['Lat'])
    params['Neighborhood'] = add_neighborhood(params['Street'])
    params['Train'] = calc_distance_from_train_station(params['Long'], params['Lat'])

    nadlan_df = pd.read_csv("data/Nadlan_clean.csv", index_col=0)
    params['Build_year'] = check_for_match(nadlan_df, params, params['Helka'], 'Build_year', 'Gush', 'Helka')

    params['Floors'] = check_for_match(nadlan_df, params, params['Helka'], 'Floors', 'Gush', 'Helka')

    params['Age'] = 2023 - params['Build_year']

    params['Street_rank'] = nadlan_df.loc[(nadlan_df['Street'] == params['Street']), 'Street_rank'].max()
    params['Gush_rank'] = nadlan_df.loc[(nadlan_df['Gush'] == params['Gush']), 'Gush_rank'].max()

    params['Helka_rank'] = check_for_match(nadlan_df, params, params['Helka'], 'Helka_rank', 'Gush', 'Helka')

    params['Neighborhood_rank'] = nadlan_df.loc[(nadlan_df['Neighborhood'] == params['Neighborhood']), 'Neighborhood_rank'].max()

    # handle missing valuses Naive solution
    for param in params:
        if params[param] is np.nan:
            print(f'None :{param}')
            params[param] = int(nadlan_df[param].mean())

    return params


def predict_apt_price(params, model):
    X = pd.DataFrame([params])

    X['Lat'] = X['Lat'].astype(np.int32)
    X['Long'] = X['Long'].astype(np.int32)
    X['Distance_sea'] = X['Distance_sea'].astype(np.int32)
    # Price

    X = X.reindex(columns=["Rooms", "Floor", "Size", "Build_year", "Floors", "Long", "Lat",
                           "Year", "Distance_sea", "Train", 'Age', 'Neighborhood_rank', 'Street_rank', 'Gush_rank',
                           'Helka_rank'])
    print(X)
    scaler = joblib.load('static/scaler.pkl')
    X_scaled = scaler.transform(X)

    # Predict prices using the trained model
    y_pred = model.predict(X_scaled)
    y_pred = y_pred * 1.02
    appraised_price = int(y_pred[0])

    return appraised_price



def Price_Increases_Neighborhood(df, neighborhood):
    years = range(2017, 2024)
    price_per_meter_by_year = {}
    for year in years:
        year_data = df[(df["Neighborhood"] == neighborhood) & (df['Year'] == year)]
        if year_data.shape[0] > 10:
            average_price_per_meter = year_data['Price'].sum() / year_data['Size'].sum()
            price_per_meter_by_year[year] = round(average_price_per_meter)

    plt.figure(figsize=(7, 3))
    bars = tuple(price_per_meter_by_year.keys())
    x_pos = np.arange(len(bars))
    plt.bar(x_pos, price_per_meter_by_year.values(), color='g', width=0.5)
    plt.xticks(x_pos, bars, rotation=10, color='c')
    text = f"מחיר למטר לפני שנים - {neighborhood} - תל אביב "
    plt.title(text[::-1], fontsize=15)
    plt.xlabel("Year", color='k', fontsize=3)
    plt.ylabel("Price per meter")
    # Save the plot as an image
    buffer = io.BytesIO()
    plt.savefig(buffer, format='png')
    buffer.seek(0)

    plot_image = base64.b64encode(buffer.getvalue()).decode('utf-8')

    plt.close()  # Close the plot to free up memory
    return plot_image


# from django.db import connection
# def db_to_df(table_name):
#     # Execute the SELECT query
#     with connection.cursor() as cursor:
#         cursor.execute(f"SELECT * FROM {table_name}")
#
#         # Fetch all the rows from the cursor
#         rows = cursor.fetchall()
#         # Get the column names from the cursor description
#         column_names = [desc[0] for desc in cursor.description]
#
#     # Create a DataFrame from the rows and column names
#     df = pd.DataFrame(rows, columns=column_names)
#     return df