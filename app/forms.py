from allauth.account.forms import SignupForm
from django import forms
from app import models as apmodels
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm



class updatecontactdetails(forms.ModelForm):
    class Meta:
        model = apmodels.Customer
        fields = ('phone_number_1','city','nearest_bus_stop','state','lga','street','street_number',)


