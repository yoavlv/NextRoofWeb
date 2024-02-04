from django.urls import path, re_path

from core.main.calculator.calculator_view import asset_value_view

from .utils.sql_utils import get_neighborhoods_for_city, get_streets_for_city, get_streets_for_neighborhood
from .views.map_view import city_details, city_plot_map, map_view, neighborhood_plot_map, street_plot_map, update_map
from .views.post_form import create_post
from .views.proflie_view import edit_profile, profile_view
# from core.main.calculator.api_view import predict_price
from .views.search_view import home, search_apartments
from .views.user_view import login_view, logout_view, register, toggle_like

urlpatterns = [
    path("", home, name="home"),
    path("search/", search_apartments, name="search"),
    path("login/", login_view, name="login"),
    path("asset_value/", asset_value_view, name="asset_value"),
    # path('api/', predict_price, name='predict_price'),
    path('post/', create_post, name='create_post'),
    path('register/', register, name='register'),
    path('logout/', logout_view, name='logout'),
    path('edit_profile/', edit_profile, name='edit_profile'),
    path('profile/', profile_view, name='profile'),
    path('get-neighborhoods/',
         get_neighborhoods_for_city,
         name='get-neighborhoods'),
    path('get-streets/', get_streets_for_neighborhood, name='get-streets'),
    path('get-streets-city/', get_streets_for_city, name='get-streets-city'),
    path('toggle_like/<str:item_id>/', toggle_like, name='toggle_like'),
    path('map/', map_view, name='map'),
    path('update_map/', update_map, name='update_map'),
    path('city/<str:city_name>/', city_details, name='city_details'),
    re_path(r'^city_plot_map/(?P<city_name>[\w\s-]+)/$',
            city_plot_map,
            name='city_plot_map'),
    re_path(
        r'^neighborhood_plot_map/(?P<city_name>[\w\s-]+)/(?P<neighborhood_name>[\w\s-]*)/$',
        neighborhood_plot_map,
        name='neighborhood_plot_map'),
    re_path(
        r'^street_plot_map/(?P<city_name>[\w\s-]+)/(?P<street_name>[\w\s-]*)/$',
        street_plot_map,
        name='street_plot_map'),

    # path('toggle_like/<int:apartment_id>/', toggle_like, name='toggle_like'),

    # Add a URL pattern with parameters for the search_apartments function
    path(
        "search/<str:area>/<str:city>/<str:neighborhood>/<str:street>/<str:room_number>/<str:min_price>/<str:max_price>/<str:sort_option>/",
        search_apartments,
        name="search_with_params"),
]
