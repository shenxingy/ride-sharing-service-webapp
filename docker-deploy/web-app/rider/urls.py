from django.urls import path
from .views import request_ride, get_eta, rider_dashboard, join_ride, edit_ride

urlpatterns = [
    path("request/", request_ride, name="request_ride"),
    path("dashboard/", rider_dashboard, name="rider_dashboard"),
    path("join/<int:ride_id>/", join_ride, name="join_ride"),
    path("edit/<int:ride_id>/", edit_ride, name="edit_ride"),  
    path("get_eta/", get_eta, name="get_eta"),
]