from django.urls import path
from . import views

urlpatterns = [
    path('dashboard/', views.rider_dashboard, name='rider_dashboard'),
    path('request/', views.request_ride, name='request_ride'),
    path('join/<int:ride_id>/', views.join_ride, name='join_ride'),
] 
