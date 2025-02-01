from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def driver_dashboard(request):
    return render(request, 'driver/dashboard.html')
