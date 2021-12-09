from django.core.exceptions import ValidationError
from functools import reduce
import math
from django.contrib.auth.hashers import make_password,check_password
from typing import Text
from django.db.models.enums import Choices
from django.db.models.fields import TextField
# from django.utils.translation import Trans
from django_countries.fields import CountryField
from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import (
    get_available_image_extensions,
    FileExtensionValidator,
)
from django.contrib.auth.models import AnonymousUser, User
from django.forms import ModelForm
from django import forms
import datetime
from django.shortcuts import get_object_or_404
from imagekit.models import ImageSpecField # < here
from pilkit.processors import ResizeToFill
from random import random
from tinymce.models import HTMLField
import os
import base64
from django.conf import settings
from django.core.exceptions import ObjectDoesNotExist
# from users import models as cmodels
from general import models as gmodels
from django.utils.timezone import now
from general import models as gmodels


def getStoreDetails():
    try:
        store = list(gmodels.General.objects.all())[0]
        return store
    except IndexError:
        store =[]



class VisitorsLog(models.Model):
    ip_1 = models.TextField(default='',max_length = 200,blank=False)
    ip_2 = models.TextField(default='',max_length = 200,blank=False)
    ip_3 = models.TextField(default='',max_length = 200,blank=False)
    host_name = models.TextField(default='',max_length = 200,blank=False)
    url = models.URLField(blank=False)
    date_time_added = models.DateTimeField(auto_now=True,blank=True)
    customerid=models.CharField(default='',max_length=50,blank=True)
    location = models.TextField(max_length=1000,default='',blank=True)

    def __str__(self):
        return self.ip_1 or self.ip_2

    # def save(self,*args,*kwargs):




class Customer(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE, default='',blank=True,editable=False)
    full_name = models.CharField(max_length=550,default='',blank=True)
    transaction_pin = models.CharField(max_length=5,default='',blank=True)
    # marital_status = models.CharField(max_length =225, choices=(('S','Single'), ('M','Married'),('D','Divorced'), ('W','Widowed'),('P','Private')), default='',blank=False)
    savings_rating = models.IntegerField(default=0)
    credit_rating = models.IntegerField(default=5)
    gender = models.CharField(max_length =225, choices=(('M','Male'), ('F','Female')), default='',blank=False)
    date_of_birth = models.DateField(auto_now=False,default=now)
    photo = models.ImageField(upload_to="media/customers/photo", blank=True)
    customerid = models.CharField(max_length=255, default='',blank=True,editable=False)
    profile_edit_date = models.DateField(auto_now=True)
    email_confirmed = models.BooleanField(default=False)
    date_time_added = models.DateTimeField(default=now)
    secret_question = models.CharField(max_length=225,blank=True,default='')
    secret_answer = models.CharField(max_length=225,blank=True,default='')
    previous_email = models.CharField(max_length=225,blank=True,default='')
    last_token = models.CharField(max_length=225,blank=True,default='')
    profile_updated = models.BooleanField(default=False)
    suspension_count = models.IntegerField(default=0)
    briefly_suspended = models.BooleanField(default=False)
    time_suspended = models.DateTimeField(auto_now_add=False,default=now, blank=True)
    time_suspended_timestamp = models.IntegerField(default=0,blank=True)
    reference_code = models.CharField(max_length=225,default='',blank=True)
    street_number = models.CharField(max_length=225, default='',blank=False)
    street = models.CharField(max_length=225, default='',blank=False)
    landmark = models.CharField(max_length=225, default='',blank=True)
    nearest_bus_stop = models.CharField(max_length=225, default='',blank=True)
    city = models.CharField(max_length=225, default='',blank=False)
    lga = models.CharField(max_length=225, default='',blank=True)
    country = CountryField(default='',blank_label='(select country)')
    state = models.CharField(max_length=225, default='',blank=False)
    full_address = models.CharField(default='',blank=True,max_length=500)
    currency =  models.CharField(default='',choices=(('NGN','Naira'), ('USD','Dollar'),('GBP','Pounds'), ('EUR','Euro')), blank=True,max_length=500)
    temporary_password =  models.BooleanField(default=False)
    middle_name = models.CharField(max_length=45, blank=True, default ='')
    first_name = models.CharField(max_length=255, blank=True, default ='')
    last_name = models.CharField(max_length=255, blank=True, default ='')
    email = models.CharField(max_length=255, blank=True, default='')
    call_code = models.CharField(max_length=5, blank=True, default ='')
    phone_number_1 = models.CharField(max_length=45, blank=True, default ='')
    phone_number_2 = models.CharField(max_length=45, blank=True, default ='')
    address1 = models.CharField(max_length=200, blank=True, default ='')
    address2 = models.CharField(max_length=200, blank=True, default ='')
    city_code = models.CharField(max_length=45, blank=True, default ='')
    country_code = models.CharField(max_length=45, blank=True, default ='')
    del_flg = models.BooleanField(default=False)
    transaction_pin_set = models.BooleanField(default=False)
    privacy_terms_accepted = models.BooleanField(default=False)
    bvn_verified = models.BooleanField(default=False)
    business_mode = models.BooleanField(default=False)
    loansecure_accepted = models.BooleanField(default=False)
    can_withdraw = models.BooleanField(default=False)
    can_transfer = models.BooleanField(default=False)
    contact_ready = models.BooleanField(default=False)
    locked = models.BooleanField(default=False)


    def __str__(self):
        return str(self.first_name) + ' ' +str(self.last_name)
       

    def save(self,*args, **kwargs):

        if self.suspension_count>2:
            self.briefly_suspended = True
            self.time_suspended =  datetime.datetime.now()
            self.time_suspended_timestamp = datetime.datetime.now().timestamp()
        secret_question=''
        for char in self.secret_question:
            if char ==  '?':
                continue
            else:
                secret_question = secret_question +char
        self.secret_question = secret_question+'?'
        self.full_address = self.street_number +', '+self.street+ ', '+self.nearest_bus_stop+'bus-stop, '+self.city +', ' +self.state
        self.full_name = self.first_name +' ' +self.last_name
        super(Customer,self).save()


class MeasurementUnit(models.Model):
    unit =models.CharField(default='', max_length=100,blank=True,)

    def __str__(self) -> str:
        return self.unit


class Tag(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
  
    def __str__(self):
        return self.name


class ProductVariation(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
    image = models.ImageField(upload_to="media/best_deals/photo", blank=True)
    description = HTMLField(default='',blank=True)
    price = models.IntegerField(default=0,blank=True)
    purchase_count = models.IntegerField(default=0,blank=True)
    formatted_price =models.CharField(default='',max_length=100,blank=True,)

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        self.formatted_price = 'NGN {:,.2f}'.format(self.price)
        # if self.productid == '':
        #     TIDtemp = getStoreDetails().store_name[0]+''+str(round(random()*1234567890))
        #     self.productid=TIDtemp[0:5]+'00'+str(Product.objects.all().count()+1)
        
        super(ProductVariation,self).save(*args, **kwargs)  



class Product(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
    image = models.ImageField(upload_to="media/best_deals/photo", blank=True)
    description = HTMLField(default='',blank=True)
    discount = models.IntegerField(default=0,blank=True)
    discount_price = models.IntegerField(default=0,blank=True)
    price = models.IntegerField(default=0,blank=True)
    rating = models.IntegerField(default=0,blank=True)
    purchase_count = models.IntegerField(default=0,blank=True)
    date_time_added = models.DateTimeField(auto_now=False,editable=True,default=now())
    view_count = models.IntegerField(default=0,blank=True)
    formatted_price =models.CharField(default='',max_length=100,blank=True,)
    formatted_discount_price =models.CharField(default='',max_length=100,blank=True,)
    productid =models.CharField(default='',max_length=100,blank=True,)
    measurement_unit =models.ForeignKey(MeasurementUnit,on_delete=models.DO_NOTHING,null=True,blank=False)
    variations = models.ManyToManyField(ProductVariation,default='',blank=True)
    tags = models.ManyToManyField(Tag,default='',blank=True)
    best_deal = models.BooleanField(default=False)
    special_package = models.BooleanField(default=False)

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        if self.discount:
            self.discount_price = self.discount/100 * self.price
        elif self.discount_price:
            self.discount =100 - (100 *self.discount_price / self.price)
        self.formatted_price = 'NGN {:,.2f}'.format(self.price)
        self.formatted_discount_price = 'NGN {:,.2f}'.format(self.discount_price)
        if self.productid == '':
            TIDtemp = getStoreDetails().store_name[0]+''+str(round(random()*1234567890))
            self.productid=TIDtemp[0:5]+'00'+str(Product.objects.all().count()+1)
        
        super(Product,self).save(*args, **kwargs)  




class ProductGroup(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
    image = models.ImageField(upload_to="media/product_groups/photo", blank=True)
    products = models.ManyToManyField(Product,default='',blank=True)


    def __str__(self):
        return self.name

class HomePageGroup(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
    products = models.ManyToManyField(Product,default='',blank=True)
    slug = models.SlugField(default='',blank=True)
    header_background_color = models.CharField(max_length=255, default='white')
    header_text_color = models.CharField(max_length=255, default='black')
    index = models.IntegerField(default=1,blank=True)
    def __str__(self):
        return self.name

    def save(self,*args, **kwargs):
        self.slug = slugify(self.name)
        super(HomePageGroup,self).save(*args, **kwargs)  

class Brand(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
    image = models.ImageField(upload_to="media/product_groups/photo", blank=True)
    products = models.ManyToManyField(Product,default='',blank=True)
    slug = models.SlugField(default='',blank=True)

    def __str__(self):
        return self.name

    def save(self,*args, **kwargs):
        self.slug = slugify(self.name)
        super(Brand,self).save(*args, **kwargs)

class BestDeal(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
    image = models.ImageField(upload_to="media/best_deals/photo", blank=True)
    products = models.ManyToManyField(Product,default='',blank=True)

    description = HTMLField(default='')

    def __str__(self):
        return self.name

class CartedProduct(models.Model):
    product =models.ForeignKey(Product,on_delete=models.CASCADE,default='')
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,default='',null=True,blank=True)
    session = models.TextField(max_length=500,default='',blank=True)
    quantity = models.IntegerField(default=0,blank=True)
    formatted_quantity =models.CharField(default='',max_length=100,blank=True,)
    amount = models.IntegerField(default=0,blank=True)
    formatted_amount =models.CharField(default='',max_length=100,blank=True,)
    cartedproductid =models.CharField(default='',max_length=100,blank=True,)
    variation = models.ForeignKey(ProductVariation,default='',blank=True,on_delete=models.CASCADE,null=True)

    def __str__(self):
        return self.product.name

    def save(self,*args,**kwargs):
        price =False
        try:
            if self.variation:
                price =self.variation.price
        except ValueError:  
            pass
        try:
            flashsales = FlashSale.objects.filter(end_date_time__gte=now())[0]
            for product in flashsales.products.all():
                if product.product == self.product:
                    price = product.price
        except Exception:
            price = self.product.price

        if price:
            pass
        else:
            price = self.product.price
  
        self.amount = self.quantity * price
        try:
            measurement_unit = self.product.measurement_unit.unit or 'None'
        except AttributeError:
            measurement_unit =' '
        if self.quantity > 1:
            measurement_unit = measurement_unit+'s'
        self.formatted_quantity = '{:,.2f}'.format(self.quantity)+' '+measurement_unit
        
        self.formatted_amount = 'NGN  {:,.2f}'.format(self.amount)
        if self.cartedproductid == '':
            TIDtemp = getStoreDetails().store_name[0]+'CP'+str(round(random()*1234567890))
            self.cartedproductid=TIDtemp[0:5]+'00'+str(CartedProduct.objects.all().count()+1)
        super(CartedProduct,self).save(*args,**kwargs)  


class DeliveryLocation(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
    price = models.IntegerField(default=0,blank=True)
    formatted_price =models.CharField(default='',max_length=100,blank=True,)
    locationid =models.CharField(default='',max_length=100,blank=True,)

    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        self.formatted_price = 'NGN {:,.2f}'.format(self.price)
        if self.locationid == '':
            TIDtemp = getStoreDetails().store_name[0]+''+str(round(random()*1234567890))
            self.locationid=TIDtemp[0:5]+'00'+str(DeliveryLocation.objects.all().count()+1)
        
        super(DeliveryLocation,self).save(*args, **kwargs)  



class Saved(models.Model):
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE,default='',null=True,blank=True)
    session = models.TextField(max_length=500,)
    products = models.ManyToManyField(Product,default='',blank=True)
    saveid =models.CharField(default='',max_length=100,blank=True,)
    date_time_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.saveid

    def save(self,*args,**kwargs):
        super(Saved,self).save(*args, **kwargs) 
        if self.saveid == '':
            TIDtemp = getStoreDetails().store_name[0]+'S'+str(round(datetime.datetime.now().timestamp()))
            TID=''
            for char in range(len(TIDtemp)):
                if TIDtemp[char] == '-' or TIDtemp[char] == ':' or TIDtemp[char] == '+'or TIDtemp[char] == '.' or TIDtemp[char] == ' ':
                    continue
                else:
                    TID = TID+TIDtemp[char]
            self.saveid=TID[0:100]+'00'+str(Saved.objects.all().count()+1)

        super(Saved,self).save() 


class Cart(models.Model):
    customer = models.OneToOneField(Customer,on_delete=models.CASCADE,default='',null=True,blank=True)
    session = models.TextField(max_length=500,)
    products = models.ManyToManyField(CartedProduct,default='',blank=True)
    total = models.IntegerField(default=0,blank=True)
    formatted_total =models.CharField(default='',max_length=100,blank=True,)
    cartid =models.CharField(default='',max_length=100,blank=True,)
    date_time_added = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.cartid

    def save(self,*args,**kwargs):
        super(Cart,self).save(*args, **kwargs) 

        total = 0
        for product in self.products.all():
            total+=product.amount
        self.total = total
        self.formatted_total = '{:,.2f}'.format(self.total)
        if self.cartid == '':
            TIDtemp = getStoreDetails().store_name[0]+'C'+str(round(datetime.datetime.now().timestamp()))
            TID=''
            for char in range(len(TIDtemp)):
                if TIDtemp[char] == '-' or TIDtemp[char] == ':' or TIDtemp[char] == '+'or TIDtemp[char] == '.' or TIDtemp[char] == ' ':
                    continue
                else:
                    TID = TID+TIDtemp[char]
            self.cartid=TID[0:100]+'00'+str(Cart.objects.all().count()+1)

        super(Cart,self).save() 


class Order(models.Model):
    customer = models.ForeignKey(Customer,on_delete=models.CASCADE,default='',null=True,blank=True)
    session = models.TextField(max_length=500,)
    products = models.ManyToManyField(CartedProduct,default='',blank=True)
    total = models.IntegerField(default=0,blank=True)
    formatted_total =models.CharField(default='',max_length=100,blank=True,)
    orderid =models.CharField(default='',max_length=100,blank=True,)
    payment_method = models.CharField(default='',max_length=100,blank=True,choices=(('op','op'),('pd','pd')))
    delivery_option = models.CharField(default='',max_length=100,blank=True,choices=(('p','p'),('d','d')))
    delivery_location = models.ForeignKey(DeliveryLocation,on_delete=models.CASCADE,default='',null=True)
    date_time_added = models.DateTimeField(auto_now=True)
    date_time_paid =models.DateTimeField(auto_now=False,default=now, blank=True)
    paid=models.BooleanField(default=False)
    complete=models.BooleanField(default=False)
    deleted=models.BooleanField(default=False)
    def __str__(self):
        return self.orderid

    def save(self,*args,**kwargs):
        super(Order,self).save(*args, **kwargs) 

        total = 0
        for product in self.products.all():
            total+=product.amount
        if self.delivery_option == 'd':
            if self.delivery_location:
                total += self.delivery_location.price
        self.total = total
        self.formatted_total = '{:,.2f}'.format(self.total)
        if self.orderid == '':
            TIDtemp = getStoreDetails().store_name[0]+'O'+str(round(datetime.datetime.now().timestamp()))
            TID=''
            for char in range(len(TIDtemp)):
                if TIDtemp[char] == '-' or TIDtemp[char] == ':' or TIDtemp[char] == '+'or TIDtemp[char] == '.' or TIDtemp[char] == ' ':
                    continue
                else:
                    TID = TID+TIDtemp[char]
            self.orderid=TID[0:100]+'00'+str(Order.objects.all().count()+1)

        super(Order,self).save() 



class ProductImage(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
    image = models.ImageField(upload_to="media/best_deals/photo", blank=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,default='')
    flip = models.BooleanField(default=False)
    def __str__(self):
        return self.name



class SlideShow(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
    image = models.ImageField(upload_to="media/slideshows/photo", blank=True)
    description = HTMLField(default='',blank=True)
    price = models.IntegerField(default=0,blank=True)
    formatted_price =models.CharField(default='',max_length=100,blank=True,)
    productid =models.CharField(default='',max_length=100,blank=True,)
    products = models.ManyToManyField(Product,default='',blank=True)
    slug = models.SlugField(default='',blank=True)
    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        self.formatted_price = '{:,.2f}'.format(self.price)
        self.slug = slugify(self.name)
        if self.productid == '':
            TIDtemp = getStoreDetails().store_name[0]+''+str(round(random()*1234567890))
            self.productid=TIDtemp[0:5]+'00'+str(SlideShow.objects.all().count()+1)
        
        super(SlideShow,self).save(*args, **kwargs)



class FlashSaleProduct(models.Model):
    price = models.IntegerField(default=0,blank=True)
    formatted_price =models.CharField(default='',max_length=100,blank=True,)
    discount = models.IntegerField(default=0,blank=True)
    product = models.ForeignKey(Product,on_delete=models.CASCADE,null=True, default='',blank=True)

    def __str__(self):
        return self.product.name

    def save(self,*args,**kwargs):
        if self.discount:
            self.price =self.product.price-(self.discount/100 * self.product.price)
        elif self.price:
            self.discount =100 -(100 * self.price/ self.product.price)
        self.formatted_price = 'NGN {:,.2f}'.format(self.price)

        super(FlashSaleProduct,self).save(*args, **kwargs)


class FlashSale(models.Model):
    name =models.CharField(default='',max_length=100,blank=True,)
    products = models.ManyToManyField(FlashSaleProduct,default='',blank=True)
    start_date_time = models.DateTimeField(default=now(),blank=True,)
    end_date_time = models.DateTimeField(default=now(),blank=True,)
    start_time_timestamp = models.IntegerField(default=0,blank=True)
    def __str__(self):
        return self.name

    def save(self,*args,**kwargs):
        self.start_time_timestamp = self.end_date_time.timestamp()
        super(FlashSale,self).save(*args, **kwargs)

    def clean(self):
        """
        Throw ValidationError if you try to save more than one model instance
        See: http://stackoverflow.com/a/6436008
        """
        model =self.__class__
        if (len(list(model.objects.filter(end_date_time__gte=now())))) > 0:
            raise ValidationError(
                "Already running %s." % model.__name__)


class NewsLetterSubscription(models.Model):
    email =models.EmailField(default='',blank=True,)
    
    def __str__(self):
        return self.email