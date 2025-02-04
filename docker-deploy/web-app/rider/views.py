import os
import json
import requests
from django.http import JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.csrf import csrf_exempt
from dotenv import load_dotenv
from .forms import RideRequestForm, JoinRideForm
from .models import Ride, RideShare

# Load environment variables
load_dotenv()
GOOGLE_MAPS_API_KEY = os.getenv("GOOGLE_MAPS_API_KEY")

def get_estimated_time(pickup, dropoff):
    """Fetch estimated time using Google Maps Distance Matrix API."""
    url = f"https://maps.googleapis.com/maps/api/distancematrix/json?origins={pickup}&destinations={dropoff}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    result = response.json()

    if result.get("status") == "OK":
        return result["rows"][0]["elements"][0]["duration"]["text"]
    return "Unknown ETA"

@csrf_exempt
def get_eta(request):
    """API Endpoint to get estimated travel time via AJAX."""
    if request.method == "POST":
        try:
            # Handle JSON or Form Data
            try:
                data = json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({"success": False, "error": "Invalid JSON data."}, status=400)

            pickup = data.get("pickup_location")
            dropoff = data.get("dropoff_location")

            if not pickup or not dropoff:
                return JsonResponse({"success": False, "error": "Invalid locations."}, status=400)

            estimated_time = get_estimated_time(pickup, dropoff)

            if estimated_time:
                return JsonResponse({"success": True, "estimated_time": estimated_time})
            else:
                return JsonResponse({"success": False, "error": "Failed to retrieve ETA."}, status=500)

        except Exception as e:
            return JsonResponse({"success": False, "error": str(e)}, status=500)

    return JsonResponse({"success": False, "error": "Invalid request method."}, status=405)

@login_required
def rider_dashboard(request):
    """Display user's rides: separate open (active) and closed (completed/cancelled) rides."""
    open_rides = Ride.objects.filter(
        rider=request.user,
        status__in=['PENDING', 'CONFIRMED']
    ).order_by('-created_at')

    closed_rides = Ride.objects.filter(
        rider=request.user,
        status__in=['COMPLETED', 'CANCELLED']
    ).order_by('-created_at')

    return render(request, 'rider/dashboard.html', {
        'open_rides': open_rides,
        'closed_rides': closed_rides
    })
    
@login_required
def request_ride(request):
    """Handles ride requests and provides an estimated arrival time."""
    if request.method == 'POST':
        form = RideRequestForm(request.POST)
        if form.is_valid():
            ride = form.save(commit=False)
            ride.rider = request.user
            ride.save()

            # Calculate estimated arrival time
            eta = get_estimated_time(ride.pickup_location, ride.dropoff_location)

            messages.success(request, f'Ride request submitted successfully! Estimated travel time: {eta}')
            return redirect('rider_dashboard')
        else:
            messages.error(request, 'There was an error in your ride request. Please check your input.')

    else:
        form = RideRequestForm()

    return render(request, 'rider/request_ride.html', {
                 "form": form,
                 "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY
        })

@login_required
def edit_ride(request, ride_id):
    """Allows users to modify their ride only if it is still PENDING."""
    ride = get_object_or_404(Ride, id=ride_id, rider=request.user, status='PENDING')

    if request.method == 'POST':
        form = RideRequestForm(request.POST, instance=ride)
        if form.is_valid():
            form.save()
            messages.success(request, "Ride updated successfully.")
            return redirect('rider_dashboard')
        else:
            messages.error(request, "There was an error updating your ride.")
    else:
        form = RideRequestForm(instance=ride)

    return render(request, 'rider/edit_ride.html', {'form': form, 'ride': ride})

@login_required
def join_ride(request, ride_id):
    """Allows a user to join an existing ride with passenger limits."""
    ride = get_object_or_404(Ride, id=ride_id, status='PENDING', allow_sharing=True)

    if request.method == 'POST':
        form = JoinRideForm(request.POST)
        if form.is_valid():
            share = form.save(commit=False)
            share.ride = ride
            share.rider = request.user

            # Calculate total passengers after joining
            total_passengers = ride.passenger_count + sum(
                share.passenger_count for share in ride.shared_rides.all()
            ) + share.passenger_count

            MAX_PASSENGERS = 4  # Set a max limit manually if no vehicle model exists
            if total_passengers > MAX_PASSENGERS:
                messages.error(request, "Ride is full. Cannot accommodate more passengers.")
                return redirect('rider_dashboard')

            ride.total_passengers = total_passengers
            ride.save()
            share.save()

            messages.success(request, 'Successfully joined the ride!')
            return redirect('rider_dashboard')
        else:
            messages.error(request, 'Invalid input. Please check your passenger count.')

    else:
        form = JoinRideForm()

    return render(request, 'rider/join_ride.html', {'form': form, 'ride': ride})