import base64
import json

import pandas as pd
from django.http import HttpResponse, JsonResponse
from django.shortcuts import redirect, render

from ...NextRoofWeb.settings.dev import get_db_engine
from ..utils.plots import city_plot, neighborhood_plot, street_plot


def read_city_rank():
    engine = get_db_engine()
    query = "SELECT * FROM city_rank"
    df = pd.read_sql_query(query, engine)
    return df


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


def city_plot_map(request, city_name):
    plot_image_city = city_plot(city_name)
    return HttpResponse(plot_image_city, content_type='text/plain')


def neighborhood_plot_map(request, city_name, neighborhood_name):
    plot_image_neighborhood = neighborhood_plot(city_name, neighborhood_name)
    return HttpResponse(plot_image_neighborhood, content_type='text/plain')


def street_plot_map(request, city_name, street_name):
    plot_image_street = street_plot(city_name, street_name)
    return HttpResponse(plot_image_street, content_type='text/plain')


def city_details(request, city_name):
    plot_image_base64 = city_plot(city_name)
    plot_image_base64 = base64.b64encode(plot_image_base64).decode('utf-8')

    # Pass the base64-encoded plot image data to the template
    context = {'city_name': city_name, 'plot_image_base64': plot_image_base64}
    return render(request, 'city_details.html', context)
