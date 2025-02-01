"""
URL configuration for rideshare_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from django.shortcuts import render
from driver.views import driver_dashboard, vehicle_registration, accept_ride
from rider.views import rider_dashboard, request_ride

def home(request):
    return render(request, 'home.html')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),
    path('driver/dashboard/', driver_dashboard, name='driver_dashboard'),
    path('driver/register-vehicle/', vehicle_registration, name='vehicle_registration'),
    path('driver/accept-ride/<int:ride_id>/', accept_ride, name='accept_ride'),
    path('rider/dashboard/', rider_dashboard, name='rider_dashboard'),
    path('rider/request-ride/', request_ride, name='request_ride'),
    path('', home, name='home'),
]
