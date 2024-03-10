from django.urls import path, re_path

from .views.calculator_view import asset_value_view
from .views.dashboard_view import dashboard, fetch_data
from .views.map_view import (check_for_city, check_for_street, city_plot_map, fetch_and_process_point, map_view,
                             street_plot_map, update_map)
from .views.proflie_view import edit_profile, profile_view
from .views.search_view import home, search_apartments
from .views.user_view import login_view, logout_view, register, toggle_like

urlpatterns = [
    path("", home, name="home"),
    path("search/", search_apartments, name="search"),
    path("login/", login_view, name="login"),
    path("asset_value/", asset_value_view, name="asset_value"),
    # path('api/', predict_price, name='predict_price'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('profile/', profile_view, name='profile'),
    path('dashboard/', dashboard, name='dashboard'),
    re_path(r'^check_for_city/(?P<city_name>[\w\s-]+)/$',
            check_for_city,
            name='check_for_city'),
    re_path(
        r'^check_for_street/(?P<city_name>[\w\s-]+)/(?P<street_name>[\w\s-]+)/$',
        check_for_street,
        name='check_for_street'),
    path('fetch_data/', fetch_data, name='fetch_data'),
    path('toggle_like/<str:item_id>/', toggle_like, name='toggle_like'),
    path('map/', map_view, name='map'),
    path('update_map/', update_map, name='update_map'),
    path('point/<str:lat>/<str:lng>/<str:radius>/', fetch_and_process_point, name='point'),
    re_path(r'^city_plot_map/(?P<city_id>\d+)/(?P<city_name>[\w\s-]+)/$',
            city_plot_map,
            name='city_plot_map'),
    re_path(
        r'^street_plot_map/(?P<city_id>\d+)/(?P<city_name>[\w\s-]+)/(?P<street_id>\d+)/(?P<street_name>[\w\s-]*)/$',
        street_plot_map,
        name='street_plot_map'),
    path(
        "search/<str:area>/<str:city>/<str:neighborhood>/<str:street>/<str:room_number>/<str:min_price>/<str:max_price>/<str:sort_option>/",
        search_apartments,
        name="search_with_params"),
]
