from django.urls import path

from core.main.calculator.calculator_view import asset_value_page, calc_asset_value

from .utils.sql_utils import get_neighborhoods_for_city, get_streets_for_city, get_streets_for_neighborhood
from .views.post_form import create_post
from .views.proflie_view import edit_profile, profile_view
# from core.main.calculator.api_view import predict_price
from .views.search_view import home, search_apartments
from .views.user_view import login_view, logout_view, register, toggle_like

urlpatterns = [
    path("", home, name="home"),
    path("search/", search_apartments, name="search"),
    path("asset_value/", asset_value_page, name="asset_value"),
    path("login/", login_view, name="login"),
    path("calc/", calc_asset_value, name="calc_asset_value"),
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

    # path('toggle_like/<int:apartment_id>/', toggle_like, name='toggle_like'),

    # Add a URL pattern with parameters for the search_apartments function
    path(
        "search/<str:area>/<str:city>/<str:neighborhood>/<str:street>/<str:room_number>/<str:min_price>/<str:max_price>/<str:sort_option>/",
        search_apartments,
        name="search_with_params"),
]
