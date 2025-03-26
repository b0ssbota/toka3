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
        fields = ['name', 'facility_type', 'location', 'additional_info']
        # We exclude date/time from the visible form, 
        # since they will be set by the modal (or hidden fields).
