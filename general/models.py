from django.db import models
from django.utils.text import slugify
from django.urls import reverse
from django.core.validators import (
    get_available_image_extensions,
    FileExtensionValidator,
)
from django.utils.timezone import now

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
from django.core.exceptions import ValidationError

class General(models.Model):
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
    phone_number_1 = models.CharField(max_length=13, default ='', blank=True, )
    phone_number_2 = models.CharField(max_length=13, default ='', blank=True, )
    address = models.CharField(max_length=1000, default ='', blank=True, )
    email = models.CharField(max_length=255, default ='', blank=True, )
    primary_color = models.CharField(max_length=255, default='chartreuse')
    background_color = models.CharField(max_length=255, default='chartreuse')
    footer_color = models.CharField(max_length=255,default='dark',choices=(('white','White'),('lighter','Light'),('dark','Dark')))
    theme = models.CharField(default='simple',max_length=100,blank=True, choices=(('simple','Simple'),('functional','Functional')))
    payment_options = models.CharField(default='both',max_length=100,blank=True, choices=(('both','Both'),('on','Online'),('od','On delivery')))
    def __str__(self):
        return self.store_name
    class Meta:
        verbose_name ='Setting'

    def clean(self):
        """
        Throw ValidationError if you try to save more than one model instance
        See: http://stackoverflow.com/a/6436008
        """
        model = self.__class__
        if (model.objects.count() > 0 and
                self.id != model.objects.get().id):
            raise ValidationError(
                "Can only create 1 instance of %s." % model.__name__)



class SocialLink(models.Model):
    name = models.CharField(max_length=255, default='Platform Name')
    color = models.CharField(max_length=1000, default='short description',blank = True)
    link = models.CharField(max_length=255, default ='', blank=True, )
    date_time_added = models.DateTimeField(auto_now=True)
    image= models.ImageField(default ='',blank=True)

    def __str__(self):
        return self.name

    def save(self):
        if 'https://' in self.link:
            pass

        else:
            self.link = 'https://'+self.link
        super(SocialLink,self).save()