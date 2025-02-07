from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vehicle
from .forms import VehicleRegistrationForm, VehicleUpdateForm
from django.contrib import messages
from rider.models import Ride
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import get_connection
import socket
from utils.gmail_service import send_email
import logging

logger = logging.getLogger(__name__)

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
        # 首先检查司机是否有车辆
        try:
            vehicle = Vehicle.objects.get(driver=request.user)
        except Vehicle.DoesNotExist:
            messages.error(request, 'You need to register a vehicle first!')
            return redirect('driver_dashboard')

        # 获取订单并检查状态
        try:
            ride = Ride.objects.get(id=ride_id)
            if ride.status != 'PENDING':
                messages.error(request, 'This ride is no longer available.')
                return redirect('driver_dashboard')
        except Ride.DoesNotExist:
            messages.error(request, 'Ride not found.')
            return redirect('driver_dashboard')

        total_passengers = ride.total_passengers if ride.total_passengers > 0 else ride.passenger_count
        
        if total_passengers <= vehicle.max_passengers:
            ride.vehicle = vehicle
            ride.status = 'CONFIRMED'
            ride.save()
            
            # 发送邮件通知
            if ride.rider and ride.rider.email:
                try:
                    logger.info("Attempting to send email...")
                    subject = "Your Ride Has Been Accepted"
                    message = f"""Dear User,

                    Your ride has been accepted by driver {vehicle.driver.username}.
                    The driver will provide service shortly.

                    Ride Details:
                    - Pickup Location: {ride.pickup_location}
                    - Destination: {ride.dropoff_location}
                    - Number of Passengers: {total_passengers}

                    If you have any questions, please contact our customer service.

                    Have a great ride!"""

                    if send_email(ride.rider.email, subject, message):
                        messages.success(request, 'Ride accepted and notification sent!')
                    else:
                        messages.success(request, 'Ride accepted but email notification failed.')
                except Exception as e:
                    logger.error(f"Email error: {str(e)}")
                    messages.success(request, 'Ride accepted but email notification failed.')
            else:
                messages.success(request, 'Ride accepted!')
                
            return redirect('driver_dashboard')
        else:
            messages.error(request, 'Your vehicle cannot accommodate this many passengers.')
    except Exception as e:
        print(f"Unexpected error in accept_ride: {str(e)}")
        messages.error(request, 'An error occurred while processing your request.')
    
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

@login_required
def update_vehicle(request):
    try:
        vehicle = Vehicle.objects.get(driver=request.user)
        if request.method == 'POST':
            form = VehicleUpdateForm(request.POST, instance=vehicle)
            if form.is_valid():
                form.save()
                messages.success(request, 'Vehicle information updated successfully!')
                return redirect('driver_dashboard')
        else:
            form = VehicleUpdateForm(instance=vehicle)
        return render(request, 'driver/update_vehicle.html', {'form': form})
    except Vehicle.DoesNotExist:
        return redirect('vehicle_registration')
