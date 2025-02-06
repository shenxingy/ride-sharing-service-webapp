from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Vehicle
from .forms import VehicleRegistrationForm
from django.contrib import messages
from rider.models import Ride
from django.core.mail import send_mail
from django.conf import settings
from django.core.mail import get_connection
import socket
from utils.gmail_service import send_email

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
                    subject = "您的订单已被接单"
                    message = f"""尊敬的用户您好,
                    
您的订单已被司机 {vehicle.driver.username} 接单。
司机将尽快为您提供服务。

订单信息：
- 上车地点：{ride.pickup_location}
- 目的地：{ride.dropoff_location}
- 乘客数：{total_passengers}

如有任何问题，请及时联系我们的客服。

祝您用车愉快！"""

                    if send_email(ride.rider.email, subject, message):
                        messages.success(request, 'Ride accepted and notification sent!')
                    else:
                        messages.success(request, 'Ride accepted but email notification failed.')
                except Exception as e:
                    print(f"Email error: {str(e)}")
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
