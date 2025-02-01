from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def rider_dashboard(request):
    return render(request, 'rider/dashboard.html')
