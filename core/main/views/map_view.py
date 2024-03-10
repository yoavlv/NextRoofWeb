import json
import os

import pandas as pd
from django.conf import settings
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render
from django.views.decorators.http import require_http_methods

from ...NextRoofWeb.settings.dev import get_db_engine
from ..utils.base_utils import check_for_city_and_street_match, wgs84_to_itm
from ..utils.plots import city_plot, lasted_deals_street, street_plot
from ..utils.sql_utils import save_user_search


@require_http_methods(["GET"])
def fetch_and_process_point(request, lat, lng, radius):
    lat = float(lat)
    lng = float(lng)
    radius = float(radius)
    new_lat, new_lng = wgs84_to_itm(lat, lng)
    file_path = os.path.join(settings.BASE_DIR, 'core', 'static', 'df', 'nadlan_clean.csv')
    if not os.path.exists(file_path):
        return JsonResponse({"error": "File not found"}, status=404)

    df = pd.read_csv(file_path)

    distances_squared = (df['x'] - new_lat) ** 2 + (df['y'] - new_lng) ** 2
    within_radius = distances_squared <= radius ** 2
    df_within_radius = df[within_radius]
    df_sorted = df_within_radius.sort_values(by='date', ascending=False)
    df_limited = df_sorted.head(20)
    df_limited = df_limited.copy()
    df_limited['price'] = df_limited['price'].apply(lambda x: "{:,.0f}₪".format(x))
    json_response = df_limited.to_json(orient='records', force_ascii=False)
    decoded_json = json.loads(json_response)

    return JsonResponse(decoded_json, safe=False)


def home_page_view(request):
    # Example of fetching a default or user-selected year for map functionality
    selected_year = request.GET.get(
        'year', 2023)  # Default to 2023 if no year is specified
    selected_year = int(selected_year)

    polygons_list, max_rank, min_rank = fetch_and_process_polygons(
        selected_year)

    years = list(range(
        2010,
        2025))

    context = {
        'selected_year': selected_year,
        'years': years,
        'polygons':
        json.dumps(polygons_list
                   ),  # Ensure polygons are JSON serialized for JavaScript use
        'max_rank': max_rank,
        'min_rank': min_rank,
        # Add any other context data needed for your home page
    }

    # Render the home page with the prepared context
    return render(request, 'map_snippet.html', context)


def read_polygons(year):
    engine = get_db_engine()
    query = """
    SELECT cp.polygon, cr.rank, c.city_name
    FROM city_polygons cp
    JOIN city_rank cr ON cp.city_code = CAST(cr.city_id AS bigint)
    JOIN cities c ON cp.city_code = c.city_code
    WHERE cr.year = %s;
    """
    df = pd.read_sql_query(query, engine, params=(year, ))

    return df


def fetch_and_process_polygons(year):
    polygons = read_polygons(year)
    max_rank = int(polygons['rank'].max()) if not polygons.empty else 0
    min_rank = int(polygons['rank'].min()) if not polygons.empty else 0
    polygons_list = polygons.to_dict(orient='records')
    return polygons_list, max_rank, min_rank


def map_view(request):
    year = request.GET.get('year', 2023)
    year = int(year)

    polygons_list, max_rank, min_rank = fetch_and_process_polygons(year)

    years = [i for i in range(2010, 2025)]
    context = {
        'years': years,
        'polygons': json.dumps(polygons_list),
        'max_rank': max_rank,
        'min_rank': min_rank,
        'selected_year': year
    }
    return render(request, "map.html", context)


def update_map(request):
    year = request.GET.get('year', 2023)
    year = int(year)
    polygons_list, max_rank, min_rank = fetch_and_process_polygons(year)

    return JsonResponse({
        'polygons': polygons_list,
        'max_rank': max_rank,
        'min_rank': min_rank,
    })


def city_plot_map(request, city_id, city_name):
    plot_image_city = city_plot(city_id, city_name)
    return HttpResponse(plot_image_city, content_type='text/plain')


def street_plot_map(request, city_id, city_name, street_id, street_name):
    save_user_search(request, city_name, city_id, street_id, street_name)
    plot_image_street = street_plot(city_id, city_name, street_id, street_name)
    return HttpResponse(plot_image_street, content_type='text/plain')


def last_deals_steet(request, city_id, city_name, street_id, street_name):
    save_user_search(request, city_name, city_id, street_id, street_name)
    plot_image_street = street_plot(city_id, city_name, street_id, street_name)
    return HttpResponse(plot_image_street, content_type='text/plain')


def check_for_street(request, city_name, street_name):
    results = check_for_city_and_street_match(city_name, street_name)
    if not results['street_id']:
        return JsonResponse(
            {
                'error':
                f" {results['city_name']} {results['city_name']} הכתובת לא נמצאת מערכת "
            },
            status=404)

    last_deals = lasted_deals_street(results['city_id'], city_name,
                                     results['street_id'], street_name)
    return JsonResponse({
        'city_id': results['city_id'],
        'street_id': results['street_id'],
        'last_deals': last_deals,
    })


def check_for_city(request, city_name):
    results = check_for_city_and_street_match(city_name)

    if not results['city_id']:
        return JsonResponse(
            {
                'error':
                f" {results['city_name']} {results['city_name']} הכתובת לא נמצאת מערכת "
            },
            status=404)

    return JsonResponse({
        'city_id': results['city_id'],
    })
