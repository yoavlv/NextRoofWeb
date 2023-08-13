from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
from django.shortcuts import redirect
from .base_functions import lasted_deals_street
import math
from django.core.paginator import Paginator


def home(request):
    top_deals = get_random_deals()
    with connection.cursor() as cursor:
        cursor.execute("SELECT distinct(Neighborhood) From trans ORDER BY Neighborhood")
        neighborhoods = [neighborhood[0].replace('(', '').replace("'", "") for neighborhood in cursor.fetchall() if neighborhood[0]]

    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT distinct(Street) From trans ORDER BY Street")
        streets = [street[0].replace('(', '').replace("'", "") for street in cursor.fetchall() if street[0]]

    return render(request, "home.html", {'top_deals':top_deals ,'neighborhoods':neighborhoods ,'streets':streets})

def login(request):
    return render(request, "login.html")


def get_random_deals(num_deals=3):
    with connection.cursor() as cursor:
        cursor.execute(
            "SELECT Price, Predicted, Street, Size, Floor, Rooms,City, Neighborhood,Item_id ,Images FROM trans WHERE LENGTH(Images) > 10  ORDER BY RAND() LIMIT %s",
            (num_deals,))
        rows = cursor.fetchall()
    items = []
    for row in rows:
        price_int = int(row[0].replace(",", "").replace(" ₪", ""))
        p_change =  calculate_percentage_difference(price_int ,int(row[1]))
        format_pred = f"{row[1]:,} ₪"
        Images = row[9]
        Images = Images.split(",")
        first = 'https:'+ Images[0][2:-1]
        if len(first) < 10:
            first =None

        link = 'https://www.yad2.co.il/' + 'item/' + row[8]
        item = {
            'Price': row[0],
            'Predicted': format_pred,
            'Street': row[2],
            'Size': row[3],
            'Floor': int(row[4]),
            'Room': int(row[5]),
            'City': row[6],
            'Neighborhood':row[7],
            'link': link,
            'Images': first,
            'p_change':p_change,
        }
        items.append(item)

    return items

def calculate_percentage_difference(num1, num2):
    difference = num1 - num2
    average = (num1 + num2) / 2
    percentage_difference = (difference / average) * 100
    return round(percentage_difference, 2)

def search_apartments(request ):
    with connection.cursor() as cursor:
        cursor.execute("SELECT distinct(Neighborhood) From trans ORDER BY Neighborhood")
        neighborhoods = [neighborhood[0].replace('(', '').replace("'", "") for neighborhood in cursor.fetchall() if neighborhood[0]]


    if request.method == 'GET':
        sort_option = request.GET.get('sort')
        # city = str(request.GET.get('city')).strip()
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

        cursor = connection.cursor()
        query = "SELECT Price, Predicted, Street, Size, Floor, Rooms, City, Neighborhood, Item_id, Images FROM trans WHERE 1=1 "
        params = []
        user_search_params = {}

        # if city:
        #     query += "AND City = %s "
        #     params.append(city)

        if neighborhood:
            neighborhood = str(neighborhood).strip()
            query += "AND Neighborhood = %s "
            params.append(neighborhood)
            user_search_params['neighborhood'] = neighborhood

        if street:
            street = str(street).strip()
            query += "AND Street = %s "
            params.append(street)
            user_search_params['street'] = street

        if min_rooms:
            query += "AND Rooms >= %s "
            params.append(min_rooms)
            user_search_params['min_rooms'] = min_rooms

        if max_rooms:
            query += "AND Rooms <= %s "
            params.append(max_rooms)
            user_search_params['max_rooms'] = max_rooms

        if min_price:
            query += "AND Price >= %s "
            params.append(min_price)
            user_search_params['min_price'] = min_price

        if max_price:
            query += "AND Price <= %s "
            params.append(max_price)
            user_search_params['max_price'] = max_price

        if min_size:
            query += "AND Size >= %s "
            params.append(min_size)
            user_search_params['min_size'] = min_size

        if max_size:
            query += "AND Size <= %s "
            params.append(max_size)
            user_search_params['max_size'] = max_size

        if min_floor:
            query += "AND Floor >= %s "
            params.append(min_floor)
            user_search_params['min_floor'] = min_floor

        if max_floor:
            query += "AND Floor <= %s "
            params.append(max_floor)
            user_search_params['max_floor'] = max_floor

        if sort_option == 'price_asc':
            query += "ORDER BY Price ASC"

        if sort_option == 'price_desc':
            query += "ORDER BY Price DESC"

        cursor.execute(query, params)
        rows = cursor.fetchall()

        apartments = []
        for row in rows:
            price_int = int(row[0].replace(",", "").replace(" ₪", ""))
            p_change = calculate_percentage_difference(price_int, int(row[1]))
            format_pred = f"{row[1]:,} ₪"
            Images = row[9]
            Images = Images.split(",")
            first = 'https:' + Images[0][2:-1]


            if len(first) < 10:
                first = None

            link = 'https://www.yad2.co.il/' + 'item/' + row[8]
            apartment = {
                'Price': row[0],
                'Predicted': format_pred,
                'Street': row[2],
                'Size': row[3],
                'Floor': int(row[4]),
                'Room': int(row[5]),
                'City': row[6],
                'Neighborhood': row[7],
                'link': link,
                'Images': first,
                'p_change': p_change,
            }
            apartments.append(apartment)

        # Pagination
        paginator = Paginator(apartments, 12)  # Show 20 apartments per page
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        num_results = len(apartments)

        return render(request, 'search.html', {
            'apartments': page_obj,
            'num_results': num_results,
            'params': params,
            'user_search_params': user_search_params,
            'neighborhoods': neighborhoods,
        })
    else:
        return render(request, 'home.html', {
            'neighborhoods': neighborhoods,
            'user_search_params': {},
        })

def more_details(request):
    pass