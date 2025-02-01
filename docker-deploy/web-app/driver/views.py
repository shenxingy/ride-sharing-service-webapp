from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Vehicle
from .forms import VehicleRegistrationForm
from django.contrib import messages

@login_required
def driver_dashboard(request):
    # check if user has registered vehicle
    try:
        vehicle = Vehicle.objects.get(driver=request.user)
        return render(request, 'driver/dashboard.html', {'vehicle': vehicle})
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
