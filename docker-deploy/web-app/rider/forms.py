from django import forms
from .models import Ride, RideShare

class RideRequestForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup_location', 'dropoff_location', 'passenger_count', 'special_request', 'allow_sharing']
        widgets = {
            'special_request': forms.Textarea(attrs={'rows': 3}),
            'pickup_location': forms.TextInput(attrs={'class': 'form-control'}),
            'dropoff_location': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'allow_sharing': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class JoinRideForm(forms.ModelForm):
    class Meta:
        model = RideShare
        fields = ['passenger_count']
        widgets = {
            'passenger_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        } 
