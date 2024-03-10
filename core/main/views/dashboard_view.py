from django.db import connection
from django.http import JsonResponse
from django.shortcuts import render


def dashboard(request):
    return render(request, 'dashboard.html')


def fetch_data(request):
    # Retrieve the time range from the AJAX request
    time_range = request.GET.get('time_range')

    # Define the interval based on the time_range value
    intervals = {
        'daily': '1 DAY',
        'weekly': '1 WEEK',
        'monthly': '1 MONTH',
        'year': '1 YEAR',
        'all': None  # For 'all', we won't use a time filter
    }

    interval = intervals.get(
        time_range, None)  # Get the interval or None if time_range is invalid

    # Initial data structure to return
    data = {
        'top_cities_data': [],
        'searches_count': 0,
        'entrances_count': 0,
    }

    # Open a connection to the database
    with connection.cursor() as cursor:
        # Construct the WHERE clause based on the interval
        if interval:
            time_condition = f"WHERE us.search_time >= CURRENT_TIMESTAMP - INTERVAL '{interval}'"
        else:
            time_condition = "" if time_range == 'all' else "WHERE 1=0"  # No data for invalid time_range

        # Query to get the top cities data
        query_top_cities = f"""
            SELECT us.city_id, c.city_name, COUNT(*) AS count
            FROM user_search AS us
            JOIN cities c ON us.city_id = c.city_code
            {time_condition}
            GROUP BY us.city_id, c.city_name
            ORDER BY count DESC
            LIMIT 5
        """
        cursor.execute(query_top_cities)
        data['top_cities_data'] = cursor.fetchall()

        # Query to get the total number of searches
        query_searches_count = f"""
            SELECT COUNT(*)
            FROM user_search AS us
            {time_condition}
        """
        cursor.execute(query_searches_count)
        data['searches_count'] = cursor.fetchone()[0]

        # Query to get the total number of entrances
        # Adjust the WHERE clause for the 'entrance' table if necessary
        query_entrances_count = f"""
            SELECT COUNT(*)
            FROM entrance
            {time_condition.replace('us.search_time', 'time')}
        """
        cursor.execute(query_entrances_count)
        data['entrances_count'] = cursor.fetchone()[0]

    # Return the fetched data as a JSON response
    return JsonResponse(data)
