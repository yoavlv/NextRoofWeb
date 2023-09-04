from django.urls import path

from . import asset_value, views

urlpatterns = [
    path("", views.home, name="home"),
    path("search/", views.search_apartments, name="search"),
    path("asset_value/", asset_value.asset_value_page, name="asset_value"),
    path("login/", views.login, name="login"),
    path("calc/", asset_value.calc_asset_value, name="calc_asset_value"),
    # Add a URL pattern with parameters for the search_apartments function
    path(
        "search/<str:area>/<str:city>/<str:neighborhood>/<str:street>/<str:room_number>/<str:min_price>/<str:max_price>/<str:sort_option>/",
        views.search_apartments,
        name="search_with_params"),
]
