from allauth.account.forms import SignupForm
from django import forms
from customers import models as cmodels
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm



class updatecontactdetails(forms.ModelForm):
    class Meta:
        model = cmodels.Customer
        fields = ('phone_number_1','city','nearest_bus_stop','state','lga','street','street_number',)


