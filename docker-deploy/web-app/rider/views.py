from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .forms import RideRequestForm
from .models import Ride
from django.contrib import messages

@login_required
def rider_dashboard(request):
    user_rides = Ride.objects.filter(rider=request.user).order_by('-created_at')
    return render(request, 'rider/dashboard.html', {'rides': user_rides})

@login_required
def request_ride(request):
    if request.method == 'POST':
        form = RideRequestForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.rider = request.user
            ride.save()
            messages.success(request, 'Ride request submitted successfully!')
            return redirect('rider_dashboard')
    else:
        form = RideRequestForm()
    return render(request, 'rider/request_ride.html', {'form': form})
