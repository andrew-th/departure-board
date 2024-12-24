from django.urls import path
from . import views

urlpatterns = [
    path("departures", views.get_departures, name="get_departures"), # API route
    path("", views.index, name="index"), # frontend route
]