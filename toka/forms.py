from django import forms
from .models import ContactSubmission, FacilityBooking

class LoginForm(forms.Form):
    username = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)

class SignupForm(forms.Form):
    username = forms.CharField(max_length=100)
    email = forms.CharField(max_length=100)
    password = forms.CharField(max_length=100)

class ContactForm(forms.ModelForm):
    class Meta:
        model = ContactSubmission
        fields = ['name', 'email', 'company', 'message']



class FacilityBookingForm(forms.ModelForm):
    class Meta:
        model = FacilityBooking
        fields = [
            'name', 
            'facility_type', 
            'location', 
            'date', 
            'time', 
            'additional_info'
        ]
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date'}),
            'time': forms.TimeInput(attrs={'type': 'time'}),
        }
