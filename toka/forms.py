from django import forms
from .models import ContactSubmission

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