from django.shortcuts import render
from django.http import HttpResponse
from django.db import connection
import math
# Create your views here.

def index(request):
    top_deals = get_random_deals()
    return render(request, "home.html", {'top_deals':top_deals})


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

def search_apartments(request):
    if request.method == 'GET':
        area = request.GET.get('area')
        city = request.GET.get('city')
        neighborhood = request.GET.get('neighborhood')
        street = request.GET.get('street')
        room_number = request.GET.get('room-number')
        min_price = request.GET.get('min-price')
        max_price = request.GET.get('max-price')

        cursor = connection.cursor()
        query = "SELECT Price, Predicted, Street, Size, Floor, Rooms,City, Neighborhood,Item_id ,Images FROM trans WHERE 1=1 "
        params = []

        if area:
            query += "AND City=%s "
            params.append(area)

        if city:
            query += "AND City=%s "
            params.append(city)

        if neighborhood:
            query += f"AND Neighborhood= '{neighborhood}' "
            params.append(neighborhood)
        if street:
            query += "AND Street=%s "
            params.append(street)

        if room_number:
            query += "AND Rooms=%s "
            params.append(room_number)

        if min_price:
            query += "AND Price >= %s "
            params.append(min_price)

        if max_price:
            query += "AND Price <= %s "
            params.append(max_price)

        query += "ORDER BY RAND() LIMIT 16"
        cursor.execute(query)

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
        return render(request, 'search.html', {'apartments': apartments})

    else:
        return render(request, 'home.html')