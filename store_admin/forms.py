from allauth.account.forms import SignupForm
from django import forms
from app import models as apmodels
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.forms import ModelForm
from seller import models as smodels
from store_admin import models as admodels


class updatecontactdetails(forms.ModelForm):
    class Meta:
        model = apmodels.Customer
        fields = ('phone_number_1','city','nearest_bus_stop','state','lga','street','street_number',)


class addproduct(forms.ModelForm):
    class Meta:
        model = apmodels.Product
        fields = ('name','image','description','price','discount','best_deal','measurement_unit','weight','available_stock','tags')


class addhomegroup(forms.ModelForm):
    class Meta:
        model = apmodels.HomePageGroup
        fields = ('name','header_background_color','index','header_text_color')


class addslideshow(forms.ModelForm):
    class Meta:
        model = apmodels.SlideShow
        fields = ('name','image')


class addcategory(forms.ModelForm):
    class Meta:
        model = apmodels.Category
        fields = ('name','is_top','image','icon')

class addtag(forms.ModelForm):
    class Meta:
        model = apmodels.Tag
        fields = ('name',)


class EditProductInformation(forms.ModelForm):
    class Meta:
        model = apmodels.Product
        fields = ('name','description','price','discount','best_deal','measurement_unit','weight','available_stock','tags')


class addproductvariation(forms.ModelForm):
    class Meta:
        model = apmodels.ProductVariation
        fields = ('name','image','description','price','discount','measurement_unit','weight','available_stock')

class EditFlashSale(forms.ModelForm):
    class Meta:
        model = apmodels.FlashSale
        fields = ('start_date_time','end_date_time')


class addproductimage(forms.ModelForm):
    class Meta:
        model = apmodels.ProductImage
        fields = ('name','image','product')

class addsociallink(forms.ModelForm):
    class Meta:
        model = admodels.SocialLink
        fields = ('name','link','color')


class addmeasurementunit(forms.ModelForm):
    class Meta:
        model = apmodels.MeasurementUnit
        fields = ('unit',)

class EditStoreBranding(forms.ModelForm):
    class Meta:
        model = admodels.Store
        fields = ('primary_color','background_color','theme','logo', 'logo_icon',)

class EditStoreInformation(forms.ModelForm):
    class Meta:
        model = admodels.Store
        fields = ('store_name','phone_number','call_code','email', 'country','city','city_code','state','street','street_number',)

class EditStorePayment(forms.ModelForm):
    class Meta:
        model = admodels.Store
        fields = ('payment_manager','payment_processor','payment_options',)

class AddFlashSalesProduct(forms.ModelForm):
    class Meta:
        model = apmodels.FlashSaleProduct
        fields = ('product','discount')


class AddMeasurementUnit(forms.ModelForm):
    class Meta:
        model = apmodels.MeasurementUnit
        fields = ('name','unit')


class settings(forms.ModelForm):
    class Meta:
        model = admodels.Store
        fields = ('store_name','logo',)

class InitialSetup(forms.ModelForm):
    class Meta:
        model = admodels.Store
        fields = ('store_name','phone_number','call_code','email', 'country','city','city_code','state','street','street_number','logo',)

class SignUpForm(UserCreationForm):
    #gender = forms.CharField(label='First Name', widget = forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(label='Email')
    first_name = forms.CharField(label='First Name', widget = forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(label='Last Name', widget = forms.TextInput(attrs={'class': 'form-control'}))
    # user_id = forms.CharField(widget = forms.HiddenInput(attrs={'class': 'form-control'}),required=False,)
    # user = forms.BooleanField(label='User',required=False)
    # usertype = forms.CharField(label='First Name', widget = forms.TextInput(attrs={'class': 'form-control'})
