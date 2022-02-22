from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

from allauth.account.forms import SignupForm
from general import models as gmodels

class SignUpForm(UserCreationForm):
    #gender = forms.CharField(label='First Name', widget = forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='First Name', widget = forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Last Name', widget = forms.TextInput(attrs={'class': 'form-control'}))
    # user_id = forms.CharField(widget = forms.HiddenInput(attrs={'class': 'form-control'}),required=False,)
    # user = forms.BooleanField(label='User',required=False)
    # usertype = forms.CharField(label='First Name', widget = forms.TextInput(attrs={'class': 'form-control'})


class settings(forms.ModelForm):
    class Meta:
        model = gmodels.General
        fields = ('store_name','logo',)

class InitialSetup(forms.ModelForm):
    class Meta:
        model = gmodels.General
        fields = ('store_name','phone_number','call_code','email', 'country','city','city_code','state','street','street_number','logo',)

