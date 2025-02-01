from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .forms import RideRequestForm, JoinRideForm
from .models import Ride
from django.contrib import messages

@login_required
def rider_dashboard(request):
    user_rides = Ride.objects.filter(rider=request.user).order_by('-created_at')
    # Get available shared rides
    available_shared_rides = Ride.objects.filter(
        status='PENDING',
        allow_sharing=True
    ).exclude(rider=request.user).order_by('-created_at')
    
    return render(request, 'rider/dashboard.html', {
        'rides': user_rides,
        'shared_rides': available_shared_rides
    })

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

@login_required
def join_ride(request, ride_id):
    ride = get_object_or_404(Ride, id=ride_id, status='PENDING', allow_sharing=True)
    
    if request.method == 'POST':
        form = JoinRideForm(request.POST)
        if form.is_valid():
            share = form.save(commit=False)
            share.ride = ride
            share.rider = request.user
            
            # Calculate total passengers
            total_passengers = ride.passenger_count + sum(
                share.passenger_count for share in ride.shared_rides.all()
            ) + share.passenger_count
            
            ride.total_passengers = total_passengers
            ride.save()
            share.save()
            
            messages.success(request, 'Successfully joined the ride!')
            return redirect('rider_dashboard')
    else:
        form = JoinRideForm()
    
    return render(request, 'rider/join_ride.html', {'form': form, 'ride': ride})
