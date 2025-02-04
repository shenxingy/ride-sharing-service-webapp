import os
import json
import requests
from datetime import datetime
from django.db.models import Q
from django.conf import settings
from django.utils.timezone import now, make_aware
from datetime import timedelta
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

def get_lat_lng(address):
    url = f"https://maps.googleapis.com/maps/api/geocode/json?address={address}&key={GOOGLE_MAPS_API_KEY}"
    response = requests.get(url)
    data = response.json()
    
    if data["status"] == "OK":
        return data["results"][0]["geometry"]["location"]  # 返回 {'lat': ..., 'lng': ...}
    return None  # 地址无效

def get_optimized_route(requester_pickup, requester_dropoff, sharer_pickup, sharer_dropoff):
    """
    Uses Google Maps Directions API to determine whether a ride is along the way:
    - requester_pickup -> sharer_pickup (fixed order)
    - sharer_dropoff & requester_dropoff (Google will optimize order)
    - Validates if both requester & sharer can arrive on time.
    """
    url = "https://maps.googleapis.com/maps/api/directions/json"
    
    requester_pickup_coords = get_lat_lng(requester_pickup)
    requester_dropoff_coords = get_lat_lng(requester_dropoff)
    sharer_pickup_coords = get_lat_lng(sharer_pickup)
    sharer_dropoff_coords = get_lat_lng(sharer_dropoff)
    
    params = {
        "origin": f"{requester_pickup_coords['lat']},{requester_pickup_coords['lng']}",
        "destination": f"{requester_dropoff_coords['lat']},{requester_dropoff_coords['lng']}",
        "waypoints": f"{sharer_pickup_coords['lat']},{sharer_pickup_coords['lng']}|{sharer_dropoff_coords['lat']},{sharer_dropoff_coords['lng']}",
        "key": GOOGLE_MAPS_API_KEY
    }
    


    response = requests.get(url, params=params)
    data = response.json()

    if data.get("status") == "OK":
        legs = data["routes"][0]["legs"]
        optimized_order = data["routes"][0].get("waypoint_order", [])

        # Determine the order of drop-offs
        dropoff_points = [sharer_dropoff, requester_dropoff]
        sorted_dropoff_points = [dropoff_points[i] for i in optimized_order]

        # Extract segment travel times (convert seconds to minutes)
        requester_to_sharer_time = legs[0]["duration"]["value"] // 60  # requester -> sharer
        sharer_to_first_dropoff_time = legs[1]["duration"]["value"] // 60  # first drop-off
        first_to_second_dropoff_time = legs[2]["duration"]["value"] // 60  # second drop-off

        # Track total travel times
        travel_times = {
            "requester": requester_to_sharer_time,
            "sharer": 0
        }

        # Assign travel time based on who is dropped off first
        if sorted_dropoff_points[0] == sharer_dropoff:
            travel_times["sharer"] += sharer_to_first_dropoff_time
            travel_times["requester"] += sharer_to_first_dropoff_time + first_to_second_dropoff_time
        else:
            travel_times["requester"] += sharer_to_first_dropoff_time
            travel_times["sharer"] += sharer_to_first_dropoff_time + first_to_second_dropoff_time
        
        print(f"Calculating route: {requester_pickup} → {sharer_pickup} → {sharer_dropoff} → {requester_dropoff}")
        print(f"Google API URL: https://maps.googleapis.com/maps/api/directions/json?origin={requester_pickup}&destination={requester_dropoff}&waypoints=optimize:true|{sharer_pickup}|{sharer_dropoff}&key=YOUR_API_KEY")
        print("Google API Response:", json.dumps(response.json(), indent=4))
        return {
            "requester_duration": travel_times["requester"],
            "sharer_duration": travel_times["sharer"],
            "optimized_order": optimized_order
        }
    else:
        print("Google API Response:", json.dumps(response.json(), indent=4))
        return None  # Optimization failed

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
    """Display user's rides and allow searching for open rides."""
    open_rides = Ride.objects.filter(
        rider=request.user,
        status__in=['PENDING', 'CONFIRMED']
    ).order_by('-created_at')

    closed_rides = Ride.objects.filter(
        rider=request.user,
        status__in=['COMPLETED', 'CANCELLED']
    ).order_by('-created_at')

    search_results = []
    search_performed = False
    print("Candidate Rides:", Ride.objects.filter(status="PENDING").exclude(rider=request.user))
    
    if request.method == "GET" and "search" in request.GET:
        # 获取搜索参数
        sharer_pickup = request.GET.get("sharer_pickup", "").strip()
        sharer_dropoff = request.GET.get("sharer_dropoff", "").strip()
        earliest_arrival = request.GET.get("earliest_arrival")
        latest_arrival = request.GET.get("latest_arrival")
        passenger_count = request.GET.get("passenger_count")
        if earliest_arrival:
            try:
                earliest_arrival_dt = make_aware(datetime.strptime(earliest_arrival, "%Y-%m-%dT%H:%M"))
            except ValueError:
                print("Invalid earliest arrival format:", earliest_arrival)

        if latest_arrival:
            try:
                latest_arrival_dt = make_aware(datetime.strptime(latest_arrival, "%Y-%m-%dT%H:%M"))
            except ValueError:
                print("Invalid latest arrival format:", latest_arrival)

        # 构建基本查询（仅搜索 "PENDING" 状态的 Ride）
        query = Q(status="PENDING")


        # 获取候选行程
        candidate_rides = Ride.objects.filter(query).exclude(rider=request.user).order_by('required_arrival_time')

        # 进一步优化匹配
        valid_rides = []
        current_time = now()
        for ride in candidate_rides:
            # 计算共享路线
            route_info = get_optimized_route(
                requester_pickup=ride.pickup_location,
                requester_dropoff=ride.dropoff_location,
                sharer_pickup=sharer_pickup,
                sharer_dropoff=sharer_dropoff,
            )

            if route_info:
                requester_eta = current_time + timedelta(minutes=route_info["requester_duration"])
                sharer_eta = current_time + timedelta(minutes=route_info["sharer_duration"])

                # 确保 Sharer 和 Requester 都能按时到达
                if requester_eta <= ride.required_arrival_time and (sharer_eta <= latest_arrival_dt and sharer_eta >= earliest_arrival_dt):
                    valid_rides.append(ride)

        search_results = valid_rides
        search_performed = True

    return render(request, 'rider/dashboard.html', {
        'open_rides': open_rides,
        'closed_rides': closed_rides,
        'search_results': search_results,
        'search_performed': search_performed,
         "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY
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

    return render(request, 'rider/edit_ride.html', {
        'form': form,
        'ride': ride,
        "GOOGLE_MAPS_API_KEY": GOOGLE_MAPS_API_KEY  # Pass API key for map
    })

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