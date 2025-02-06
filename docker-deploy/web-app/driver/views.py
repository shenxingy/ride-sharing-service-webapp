from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vehicle
from .forms import VehicleRegistrationForm
from django.contrib import messages
from rider.models import Ride

@login_required
def driver_dashboard(request):
    # check if user has registered vehicle
    try:
        vehicle = Vehicle.objects.get(driver=request.user)
        # Get all pending rides and accepted rides by this driver
        pending_rides = Ride.objects.filter(status='PENDING').order_by('-created_at')
        my_rides = Ride.objects.filter(vehicle=vehicle).exclude(status='COMPLETED').order_by('-created_at')
        return render(request, 'driver/dashboard.html', {
            'vehicle': vehicle,
            'pending_rides': pending_rides,
            'my_rides': my_rides
        })
    except Vehicle.DoesNotExist:
        return redirect('vehicle_registration')

@login_required
def vehicle_registration(request):
    if request.method == 'POST':
        form = VehicleRegistrationForm(request.POST)
        if form.is_valid():
            vehicle = form.save(commit=False)
            vehicle.driver = request.user
            vehicle.save()
            messages.success(request, 'Vehicle registered successfully!')
            return redirect('driver_dashboard')
    else:
        form = VehicleRegistrationForm()
    return render(request, 'driver/vehicle_registration.html', {'form': form})

@login_required
def accept_ride(request, ride_id):
    try:
        vehicle = Vehicle.objects.get(driver=request.user)
        ride = get_object_or_404(Ride, id=ride_id, status='PENDING')
        
        total_passengers = ride.total_passengers if ride.total_passengers > 0 else ride.passenger_count
        
        if total_passengers <= vehicle.max_passengers:
            ride.vehicle = vehicle
            ride.status = 'CONFIRMED'
            ride.save()
            messages.success(request, 'Ride accepted successfully!')
        else:
            messages.error(request, 'Too many passengers for your vehicle capacity!')
            
    except Vehicle.DoesNotExist:
        messages.error(request, 'You need to register a vehicle first!')
    
    return redirect('driver_dashboard')

@login_required
def finish_ride(request, ride_id):
    try:
        vehicle = Vehicle.objects.get(driver=request.user)
        ride = get_object_or_404(Ride, id=ride_id, status='CONFIRMED', vehicle=vehicle)
        ride.status = 'COMPLETED'
        ride.save()
        messages.success(request, 'Ride completed successfully!')
    except Vehicle.DoesNotExist:
        messages.error(request, 'Vehicle not found!')
    except Ride.DoesNotExist:
        messages.error(request, 'Ride not found!')
    
    return redirect('driver_dashboard')
