from django.urls import path
from . import views
from .views import RideDetailView

urlpatterns = [
    path('dashboard/', views.driver_dashboard, name='driver_dashboard'),
    path('register/', views.vehicle_registration, name='vehicle_registration'),
    path('update/', views.update_vehicle, name='update_vehicle'),
    path('accept_ride/<int:ride_id>/', views.accept_ride, name='accept_ride'),
    path('finish_ride/<int:ride_id>/', views.finish_ride, name='finish_ride'),
    path('ride/<int:pk>/', RideDetailView.as_view(), name='ride_detail'),
] 
