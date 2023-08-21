from django.shortcuts import render
from django.http import HttpResponse
from django.shortcuts import redirect
from .base_functions import lasted_deals_street
import math
from django.core.paginator import Paginator
import pandas as pd
from datetime import datetime

t = datetime.year.__str__()

def home(request):
    top_deals = get_random_deals()
    df_history_deals = pd.read_csv('data/Nadlan_clean.csv')
    neighborhoods = sorted(set(df_history_deals['Neighborhood']))
    streets = sorted(set(df_history_deals['Street']))

    return render(request, "home.html", {'top_deals':top_deals ,'neighborhoods':neighborhoods ,'streets':streets})

def login(request):
    return render(request, "login.html")


def get_random_deals(num_deals=3):

    items = []

    df_deals = pd.read_csv('data/Predicted_DB.csv')
    df_filtered = df_deals[df_deals['Images'].apply(lambda x: len(x) > 10)]
    df_shuffled = df_filtered.sample(frac=1)
    df_shuffled = df_shuffled.head(3)
    for index, row in df_shuffled.iterrows():
        price_int = int(row['Price'].replace(",", "").replace(" ₪", ""))
        p_change = calculate_percentage_difference(price_int ,int(row['Predicted']))
        link = 'https://www.yad2.co.il/' + 'item/' + row['Item_id']
        Images = row['Images'].split(",")
        first = 'https:'+ Images[0][2:-1]
        if len(first) < 10:
            first =None
        predicted_price = f"₪{row['Predicted']:,.0f}"
        item = {
            'Price':row['Price'],
            'Predicted': predicted_price,
            'Street': row['Street'],
            'Size': row['Size'],
            'Floor': int(row['Floor']),
            'Room':  int(row['Rooms']),
            'City': row['City'],
            'Neighborhood':row['Neighborhood'],
            'link': link,
            'Images': first,
            'p_change':p_change,
        }
        items.append(item)

    return items

def calculate_percentage_difference(num1, num2):
    difference = num1 - num2
    average = (num1 + num2) / 2
    percentage_difference = ((difference / average) * 100) * -1
    return round(percentage_difference, 2)

def search_apartments(request):
    df_history_deals = pd.read_csv('data/Nadlan_clean.csv')
    neighborhoods = sorted(set(df_history_deals['Neighborhood']))
    neighborhoods.insert(0, 'בחר שכונה')
    search = False
    if request.method == 'GET':
        sort_option = request.GET.get('sort')
        neighborhood = request.GET.get('neighborhood')
        street = request.GET.get('street')
        min_rooms = request.GET.get('min-rooms')
        max_rooms = request.GET.get('max-rooms')
        min_size = request.GET.get('min-size')
        max_size = request.GET.get('max-size')
        min_price = request.GET.get('min-price')
        max_price = request.GET.get('max-price')
        max_floor = request.GET.get('max-floor')
        min_floor = request.GET.get('min-floor')

        results_df = pd.read_csv('data/Predicted_DB.csv')
        results_df_len = results_df.shape[0]

        results_df['Price_int'] = results_df['Predicted'] + results_df['Difference']
        results_df['Price_int'] = results_df['Price_int'].astype(int)
        if neighborhood:
            neighborhood = str(neighborhood).strip()
            results_df = results_df[results_df['Neighborhood'] == neighborhood]

        if street:
            street = str(street).strip()
            results_df = results_df[results_df['Street'] == street]

        if min_rooms:
            min_rooms = int(min_rooms)
            results_df = results_df[results_df['Rooms'] >= min_rooms]

        if max_rooms:
            max_rooms = int(max_rooms)
            results_df = results_df[results_df['Rooms'] <= max_rooms]

        if min_price:
            min_price = int(min_price)
            results_df = results_df[results_df['Price_int'] >= min_price]

        if max_price:
            max_price = int(max_price)
            results_df = results_df[results_df['Price_int'] <= max_price]

        if min_size:
            min_size = int(min_size)
            results_df = results_df[results_df['Size'] >= min_size]

        if max_size:
            max_size = int(max_size)
            results_df = results_df[results_df['Size'] <= max_size]

        if min_floor:
            min_floor = int(min_floor)
            results_df = results_df[results_df['Floors'] >= min_floor]

        if max_floor:
            max_floor = int(max_floor)
            results_df = results_df[results_df['Floors'] <= max_floor]

        # Apply sorting to the DataFrame
        if sort_option == 'price_asc':
            results_df = results_df.sort_values(by='Price')
        elif sort_option == 'price_desc':
            results_df = results_df.sort_values(by='Price', ascending=False)

        # Retrieve data for display
        apartments = []
        for index, row in results_df.iterrows():
            price_int = int(row['Price'].replace(",", "").replace(" ₪", ""))
            p_change = calculate_percentage_difference(price_int, int(row['Predicted']))
            link = 'https://www.yad2.co.il/' + 'item/' + row['Item_id']
            Images = row['Images'].split(",")
            first = 'https:' + Images[0][2:-1]
            if len(first) < 10:
                first = None
            predicted_price = f"₪{row['Predicted']:,.0f}"

            item = {
                'Price': row['Price'],
                'Predicted': predicted_price,
                'Street': row['Street'],
                'Size': row['Size'],
                'Floor': int(row['Floor']),
                'Room': int(row['Rooms']),
                'City': row['City'],
                'Neighborhood': row['Neighborhood'],
                'link': link,
                'Images': first,
                'p_change': p_change,
            }
            apartments.append(item)

        # Pagination
        paginator = Paginator(apartments, 12)  # Show 12 apartments per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        num_results = len(apartments)

        if results_df_len == num_results:
            search = False

        else:
            search = True

        return render(request, 'search.html', {
            'apartments': page_obj,
            'num_results': num_results,
            'neighborhoods': neighborhoods,
            'search': search,
        })
    else:
        search = False
        return render(request, 'search.html', {
            'neighborhoods': neighborhoods,
            'search':search,
        })