from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('register-vehicle/', views.vehicle_registration, name='vehicle_registration'),
    path('accept-ride/<int:ride_id>/', views.accept_ride, name='accept_ride'),
] 
