from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="idndex"),
    path("search/", views.search_apartments, name="search"),
    # Add a URL pattern with parameters for the search_apartments function
    path("search/<str:area>/<str:city>/<str:neighborhood>/<str:street>/<str:room_number>/<str:min_price>/<str:max_price>/", views.search_apartments, name="search_with_params"),
]
