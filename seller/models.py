from operator import mod
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
from django.contrib.sites.models import Site
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
# from admin.views import savedproducts
# from users import models as apmodels
from django.utils.timezone import now
from app.models import (Customer,Product,Order,Cart,CartedProduct,NewsLetterSubscription,)

class SocialLink(models.Model):
    name = models.CharField(max_length=255, default='Platform Name')
    color = models.CharField(max_length=1000, default='short description',blank = True)
    link = models.CharField(max_length=255, default ='', blank=True, )
    date_time_added = models.DateTimeField(auto_now=True)
    image= models.ImageField(default ='',blank=True)
    class Meta:
        db_table = 'sociallinks'
    def __str__(self):
        return self.name

    def save(self):
        if 'https://' in self.link:
            pass

        else:
            self.link = 'https://'+self.link
        self.name = self.name.lower()
        super(SocialLink,self).save()

class Store(models.Model):
    # user = models.OneToOneField(User,on_delete=models.DO_NOTHING,null=True, default='',blank=True,editable=False)

    store_name = models.CharField(max_length=255, default='store Name')
    store_name_prefix = models.CharField(max_length=255, default='store Name Prefix')
    logo= models.ImageField(blank=False, default ='',)
    logo_loader= models.ImageField(default ='',blank=True)
    logo_loader= models.ImageField(default ='',blank=True)
    logo_loader_text= models.ImageField(default ='',blank=True)
    payment_cards_image= models.ImageField(default ='',blank=True)
    error_404_background= models.ImageField(default ='',blank=True)
    error_500_background= models.ImageField(default ='',blank=True)
    logo_icon= models.ImageField(default ='',blank=True)
    phone_number = models.CharField(max_length=13, default ='', blank=True, )
    phone_number_2 = models.CharField(max_length=13, default ='', blank=True, )
    address = models.CharField(max_length=1000, default ='', blank=True, )
    email = models.CharField(max_length=255, default ='', blank=True, )
    call_code = models.CharField(max_length=5, blank=True, null=True, default='')
    street_number = models.CharField(max_length=225, default='',blank=False)
    street = models.CharField(max_length=225, default='',blank=False)
    city = models.CharField(max_length=225, default='',blank=False)
    country = CountryField(default='',blank_label='(select country)')
    state = models.CharField(max_length=225, default='',blank=False)
    full_address = models.CharField(default='',blank=True,max_length=500)
    city_code = models.CharField(max_length=45, blank=True, null=True, default='')
    country_code = models.CharField(max_length=45, blank=True, null=True, default='')
    primary_color = models.CharField(max_length=255, default='chartreuse')
    background_color = models.CharField(max_length=255, default='chartreuse')
    footer_color = models.CharField(max_length=255,default='dark',choices=(('white','White'),('lighter','Light'),('dark','Dark')))
    payment_manager = models.CharField(default='platform',max_length=100,blank=True, choices=(('platform','Platform'),('custom','Custom')))
    payment_processor = models.CharField(default='paystack',max_length=100,blank=True, choices=(('paystack','Paystack'),('flutterwave','Flutterwave')))
    theme = models.CharField(default='simple',max_length=100,blank=True, choices=(('simple','Simple'),('functional','Functional')))
    payment_options = models.CharField(default='both',max_length=100,blank=True, choices=(('both','Both'),('on','Online'),('od','On delivery')))
    is_ready = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    is_pending = models.BooleanField(default=False)
    products = models.ManyToManyField(Product, default='',blank=True)
    date_time_added = models.DateTimeField(auto_now=True)

    social_links = models.ManyToManyField(SocialLink,default='',blank=True) 
    news_letter_subscription = models.ManyToManyField(NewsLetterSubscription,default='',blank=True)
    orders = models.ManyToManyField(CartedProduct,default='',blank=True)
    # orders = models.ManyToManyField(Order,default='',blank=True)
    slug = models.SlugField(default='',unique=True,blank=True)
    def __str__(self):
        return self.store_name
    class Meta:
        verbose_name ='Store'
        db_table = 'stores'

    def save(self,*args,**kwargs):
        self.slug = slugify(self.store_name.lower())
        storename = str(self.store_name).strip()
        initchars = storename[0]
        for char in range(len(storename)):
            if storename[char] == ' ':
                initchars+=storename[char+1]
        self.store_name_prefix = initchars
        self.full_address = str(self.street_number) +', '+str(self.street)+ ', ' +str(self.state)+ ', ' +str(self.country.name)

        super(Store,self).save(*args,**kwargs)



class Seller(models.Model):
    user = models.OneToOneField(User,on_delete=models.CASCADE,null=True)
    store = models.OneToOneField(Store,on_delete=models.CASCADE,null=True)


