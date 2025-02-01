from django import forms
from .models import Ride

class RideRequestForm(forms.ModelForm):
    class Meta:
        model = Ride
        fields = ['pickup_location', 'dropoff_location', 'passenger_count', 'special_request']
        widgets = {
            'special_request': forms.Textarea(attrs={'rows': 3}),
            'pickup_location': forms.TextInput(attrs={'class': 'form-control'}),
            'dropoff_location': forms.TextInput(attrs={'class': 'form-control'}),
            'passenger_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
        } 
