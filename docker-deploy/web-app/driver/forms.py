from django import forms
from .models import Vehicle

class VehicleRegistrationForm(forms.ModelForm):
    class Meta:
        model = Vehicle
        fields = ['type', 'plate_number', 'max_passengers', 'special_info']
        widgets = {
            'special_info': forms.Textarea(attrs={'rows': 3}),
        }
