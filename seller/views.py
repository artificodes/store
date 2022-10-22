from app.views import logrequest
from ast import Store
import re
from django.urls.base import reverse
from django.utils.decorators import method_decorator
from django.views import View
from seller.email_sender import sendmail
from functools import reduce
import json
from typing import Match
import math
import inspect
from django.core import exceptions
from django.utils.timezone import now
import requests
from dateutil.relativedelta import relativedelta
from allauth import account
from qr_code.qrcode.utils import QRCodeOptions
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.hashers import make_password,check_password
from django.db.models import query
from django.shortcuts import render, redirect
from allauth.account.views import SignupView
from seller import forms as sforms
from wkhtmltopdf.views import PDFTemplateResponse
from wkhtmltopdf.views import PDFTemplateView
from django.core.exceptions import ObjectDoesNotExist

from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.utils.http import MONTHS, urlsafe_base64_decode
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from general.tokens import account_activation_token
import socket
import smtplib
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
from django.contrib import messages
from django.http import HttpResponse, request as django_request
from django.views import View
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
import os
import base64
from django.forms import ModelForm
from django.conf import settings
from django import forms
import datetime
import json
from allauth.account.views import AjaxCapableProcessFormViewMixin
from django.contrib.auth.decorators import login_required
from random import random
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.template import loader
from django.http import JsonResponse
from django.urls import reverse_lazy
from allauth.account import forms as allauthforms
from django.core.mail import send_mail
from store_admin import models as admodels
from seller import models as smodels
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from paystackapi.verification import Verification
from app import models as apmodels
paystack_secret_key = "sk_test_e6c40e9e83237dbb32096831467c6e6193a970cb"
paystack = Paystack(secret_key=paystack_secret_key)


allObject = {}
message = ''


def seller_login_required(function):
    
    def checkstatus(request,*args,**kwargs):
        if request.user.is_anonymous:
            return sellerlookup(request,True,*args,**kwargs)
        else:
            try:
                smodels.Seller.objects.get(user=request.user)

                return function(request,*args,**kwargs)
            except ObjectDoesNotExist:
                return sellerlookup(request,True,*args,**kwargs)
    return checkstatus

def checksellerstatus(function):
    
    def sellerstatus(request,*args,**kwargs):
        allObject = inherit(request)

        if allObject['store']:

            store = allObject['store']
        else:
            store = False
        if store:
            if store.is_ready:
                return function(request,*args,**kwargs)

        else:
            return storesetup(request,True,*args,**kwargs)
    return sellerstatus



def error500page(request, *args, **kwargs):

    allObject ={}
    try:
        settings = list(gmodels.General.objects.all())[0]
    except IndexError:
        settings =[]    
    allObject['settings'] = settings
    content_template = 'general/500.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data)

def error404page(request, *args, **kwargs):
    allObject ={}
    try:
        settings = list(gmodels.General.objects.all())[0]
    except IndexError:
        settings =[]    
    allObject['settings'] = settings

    allObject['title'] = 'Content not found'
    content_template = 'general/404.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data)      


def handler500(request, *args, **kwargs):

    return error500page(request)

def handler404(request, *args, **kwargs):

    return error404page(request)





def inherit(request):
    allObject = {}
    try:
        request.session['session_key']
    except KeyError:
        nums = '0123456789'
        tempnums = ''
        lalph = 'abcdefghijklmnopqrstuvwxyz'
        templalph=''
        ualph = lalph.upper()
        tempualph = ''

        for num in range(0,len(nums)):
            tempnums +=nums[round((random()-0.5)*len(nums))]
        for num in range(0,len(lalph)):
            templalph +=lalph[round((random()-0.5)*len(lalph))]
        for num in range(0,len(ualph)):
            tempualph +=ualph[round((random()-0.5)*len(ualph))]
        temporary_userid = tempnums[0:5] + templalph[0:7]+tempualph[0:10]
        sessionid= []
        for char in temporary_userid:
            sessionid.insert(round(random()*5),char)
        request.session['session_key'] = ''.join(sessionid)
    allObject ={}
    allObject['store'] = ''

    if request.user.is_anonymous:
        pass
    else:
        try:
            seller = smodels.Seller.objects.get(user=request.user)
            store = seller.store
            socialplatforms = smodels.SocialLink.objects.filter(store=store)
            allObject['store'] = store
            allObject['socialmediaplatforms'] = socialplatforms
        except ObjectDoesNotExist:
            pass   
        user = User.objects.get(pk=request.user.pk)

    allObject['server_timestamp'] = round(datetime.datetime.now().timestamp())
       

    site = Site.objects.get(id=1).domain
    allObject['site'] = site
    return allObject


def verifypayment(request, *args, **kwargs):
    allObject = inherit(request)
    reference = request.POST.copy().get('reference')
    notconnected = True
    while notconnected:
        try:
            verification_response = Transaction.verify(reference=reference)
            notconnected = False
        except exceptions:
            pass
    if verification_response['status']:
        template_name = 'general/success.html'
        message = "<span class='text-primary uk-text-bold h1'>Payment successful </span>"
        allObject['message'] = message
        message = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'success': True,
                        }
        return JsonResponse(output_data)  
    else:
        output_data = {
        'success': False,
                        }
        return JsonResponse(output_data)      

@seller_login_required
@checksellerstatus
def verifypaymentinine(request, reference):
    reference =reference
    notconnected = True
    while notconnected:
        try:
            verification_response = Transaction.verify(reference=reference)
            notconnected = False
        except exceptions:
            pass
    if verification_response['status'] == True:

        return True
    else:

        return False


@seller_login_required
@checksellerstatus
def confirmemail(request,updated=False, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/email_confirmation_form.html'
    return render(request,template_name,allObject)
    return JsonResponse(output_data)  




@seller_login_required
def storesetup(request,inline=False, *args, **kwargs):
    

    logrequest(request,'')
    allObject = inherit(request)

    if request.method == 'POST':
        try:
            seller = smodels.Seller.objects.get(user=request.user)
        except ObjectDoesNotExist:
            output_data = {
            'modal_message': 'User account does not exist',
                            }
            return JsonResponse(output_data)

        if seller.store:
            store = seller.store
        else:
            store = False
        if store:
            store = sforms.InitialSetup(request.POST,request.FILES,instance=store)

        else:
            store = sforms.InitialSetup(request.POST,request.FILES)
        if store.is_valid:
            storename =str(request.POST.copy().get('store_name'))
            try:
                existingstore = smodels.Store.objects.get(store_name=storename)
                message = 'Store with name '+'<b>'+ storename+'</b> already exists.'
                redirecturl = ''
            except ObjectDoesNotExist:
                store.save(commit = False)
                store = store.instance
                store.user = request.user
                store.is_ready = True
                store.save()
                seller.store=store
                seller.save()
                allObject['message'] = '<span class="text-primary uk-text-bold h1">Store setup successful</span>'
                message_template = 'general/success.html'
                # global message
                message = loader.render_to_string(message_template,allObject,request)
                redirecturl = redirect('seller_dashboard').url
            output_data = {
            'modal_message': message,
            'redirecturl':redirecturl

            # 'redirecturl':request.GET.get('next')
                            }
            return JsonResponse(output_data)
        else:
            output_data = {
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        allObject = inherit(request)
        url = str(request.get_full_path())
        store = allObject['store']

        template_name = 'seller/setup.html'
        allObject['title'] = 'DPG | Confirm email'
        allObject['page'] = 'Account activation'
        allObject['next'] = request.GET.get('next')
        content = loader.render_to_string(template_name,allObject,request)
        if inline:
            output_data = {
            'content': content,
            'title':"Store setup",
            'page':'Store setuop',

            'redirecturl':redirect('seller_store_setup').url

                            }
            return JsonResponse(output_data)
        else:
            output_data = {
            'content': content,
            'title':"Store setup",
            'page':'Store setup'
                            }
            return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def editstorebranding(request, *args, **kwargs):

    allObject = inherit(request)

    if request.method == 'POST':
        if allObject['store']:
            store = allObject['store']
            store = sforms.EditStoreBranding(request.POST,request.FILES,instance=store)

        else:

            store = sforms.InitialSetup(request.POST,request.FILES)
        if store.is_valid:
            store.save()
            store = store.instance
            store.is_ready = True
            store.save()
            message ='Store brand edited'
            content = store_branding(request,True)
            output_data = {
            'notification': message,
            'updatecontent': content,
            'container':'store_branding_inner'

                            }
            return JsonResponse(output_data) 
        else:
            output_data = {
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        allObject = inherit(request)
        url = str(request.get_full_path())
        # store = allObject['store']

        template_name = 'seller/edit_store_branding.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'modal_content': content,
        'heading':"Edit store branding",

                        }
        return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def editstorepayment(request, *args, **kwargs):

    allObject = inherit(request)

    if request.method == 'POST':
        try:
            store = smodels.Store.objects.get(user=request.user)
            store = sforms.EditStorePayment(request.POST,request.FILES,instance=store)

        except IndexError:

            store = sforms.InitialSetup(request.POST,request.FILES)
        if store.is_valid:
            store.save()
            message ='Store payment edited'
            content = store_payment(request,True)
            output_data = {
            'notification': message,
            'updatecontent': content,
            'container':'store_payment_inner'

                            }
            return JsonResponse(output_data) 
        else:
            output_data = {
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        allObject = inherit(request)
        url = str(request.get_full_path())
        store = allObject['store']

        template_name = 'seller/edit_store_payment.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'modal_content': content,
        'heading':"Edit store payment",

                        }
        return JsonResponse(output_data)



@seller_login_required
@checksellerstatus
def editstoreinformation(request, *args, **kwargs):

    if request.method == 'POST':
        try:
            store = smodels.Store.objects.get(user=request.user)
            store = sforms.EditStoreInformation(request.POST,request.FILES,instance=store)

        except IndexError:

            store = sforms.InitialSetup(request.POST,request.FILES)
        if store.is_valid:
            store.save()
            message ='Store information edited'
            content = store_information(request,True)
            output_data = {
            'notification': message,
            'updatecontent': content,
            'container':'store_information_inner'

                            }
            return JsonResponse(output_data) 
        else:
            output_data = {
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        allObject = inherit(request)
        url = str(request.get_full_path())
        store = allObject['store']

        template_name = 'seller/edit_store_information.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'modal_content': content,
        'heading':"Edit store information",

                        }
        return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def editproductinformation(request,productid=None, *args, **kwargs):
    allObject = inherit(request)

    product = apmodels.Product.objects.get(productid=productid)

    title = 'Edit Product - '+product.name

    if request.method == 'POST':
        product = sforms.EditProductInformation(request.POST,request.FILES,instance=product)
        message = 'Product edited'

        if product.is_valid:
            product.save()
            product = product.instance
            message =message
            content = product_details(request,product.productid, True)
            output_data = {
            'notification': message,
            'redirecturl': redirect('seller_product_details',productid=product.productid).url,
            'container':'app'

                            }
            return JsonResponse(output_data) 
        else:
            output_data = {
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        units = apmodels.MeasurementUnit.objects.all()
        allObject['units'] = units
        action = 'edit'
        product = apmodels.Product.objects.get(productid=productid)
        allObject['product'] = product
        title = 'Edit ' + product.name

        allObject['action'] = action

        template_name = 'seller/edit_product_information.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'content': content,
        'title': title,
        'page':title
                        }
        return JsonResponse(output_data)




@seller_login_required
@checksellerstatus
def addproduct(request,*args, **kwargs):
    # edit = request.GET.get('edit')
    # add = request.GET.get('add')
    # id =  request.GET.get('id')
    title = 'Add Product'
    allObject=inherit(request)
    store=allObject['store']
    if request.method == 'POST':
        product = sforms.addproduct(request.POST,request.FILES,)
        message = 'Product added'

        if product.is_valid:
            product.save()
            product = product.instance
            store.products.add(product)
            store.save()
            message =message
            content = product_details(request,product.productid, True)
            output_data = {
            'notification': message,
            'redirecturl': redirect('seller_product_details',productid=product.productid).url,
            'container':'app'

                            }
            return JsonResponse(output_data) 
        else:
            output_data = {
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        units = apmodels.MeasurementUnit.objects.all()
        allObject['units'] = units

        # product = apmodels.Product.objects.get(productid=id)
        # allObject['product'] = product
        title = 'Add product'


        template_name = 'seller/add_product.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'content': content,
        'title': title,
        'page':title
                        }
        return JsonResponse(output_data)



@seller_login_required
@checksellerstatus
def editproduct(request,productid=None, *args, **kwargs):
    # edit = request.GET.get('edit')
    # add = request.GET.get('add')
    # id =  request.GET.get('id')
    allObject = inherit(request)

    product = apmodels.Product.objects.get(productid=productid)

    title = 'Edit Product - '+product.name

    if request.method == 'POST':
        product = sforms.addproduct(request.POST,request.FILES,instance=product)
        message = 'Product edited'

        if product.is_valid:
            product.save()
            product = product.instance
            message =message
            content = product_details(request,product.productid, True)
            output_data = {
            'notification': message,
            'redirecturl': redirect('seller_product_details',productid=product.productid).url,
            'container':'app'

                            }
            return JsonResponse(output_data) 
        else:
            output_data = {
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        units = apmodels.MeasurementUnit.objects.all()
        allObject['units'] = units
        action = 'edit'
        product = apmodels.Product.objects.get(productid=productid)
        allObject['product'] = product
        title = 'Edit ' + product.name

        allObject['action'] = action

        template_name = 'seller/add_product.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'content': content,
        'title': title,
        'page':title
                        }
        return JsonResponse(output_data)




@seller_login_required
@checksellerstatus
def addproductvariation(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    product = apmodels.Product.objects.get(productid=productid)
    if request.method == 'POST':

        variation = sforms.addproductvariation(request.POST,request.FILES,)
        if variation.is_valid:
            variation.save()
            variation = variation.instance
            product.variations.add(variation)
            content=product_variations(request,productid,True)
            message ='Product variation added'
            output_data = {
            'notification': message,
            'updatecontent':content,
            'container':'product_variations_inner'
                            }
            return JsonResponse(output_data)
        else:
            output_data = { 
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:

        allObject = inherit(request)
        units = apmodels.MeasurementUnit.objects.all()
        allObject['units'] = units
        url = str(request.get_full_path())
        allObject['product'] = product

        template_name = 'seller/add_product_variation.html'
        allObject['next'] = request.GET.get('next')
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'modal_content': content,
        'heading': product.name +  ' - Add variation'
                        }
        return JsonResponse(output_data)



@seller_login_required
@checksellerstatus
def editproductvariation(request,productid=None,variationid=None, *args, **kwargs):
    allObject = inherit(request)
    variation = apmodels.ProductVariation.objects.get(pk=variationid)
    product = apmodels.Product.objects.get(productid=productid)
    if request.method == 'POST':

        variation = sforms.addproductvariation(request.POST,request.FILES,instance=variation)
        if variation.is_valid:
            variation.save()
            variation = variation.instance
            product.variations.add(variation)
            content=product_variations(request,productid,True)
            message ='Product variation edited'
            output_data = {
            'notification': message,
            'updatecontent':content,
            'container':'product_variations_inner'
                            }
            return JsonResponse(output_data)
        else:
            output_data = { 
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        allObject = inherit(request)
        url = str(request.get_full_path())
        allObject['product'] = product
        allObject['variation'] = variation

        template_name = 'seller/add_product_variation.html'
        allObject['next'] = request.GET.get('next')
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'modal_content': content,
        'heading': 'Edit variation - '+variation.name 
                        }
        return JsonResponse(output_data)



@seller_login_required
@checksellerstatus
def addsocialink(request, *args, **kwargs):
    edit = request.GET.get('edit')
    add = request.GET.get('add')
    id =  request.GET.get('id')
    action = 'add'
    store = smodels.Store.objects.get(user=request.user)
    if request.method == 'POST':
        if edit:
            social = gmodels.SocialLink.objects.get(pk=id)
            link = sforms.addsociallink(request.POST,request.FILES,instance=social)
            message = 'Link edited'
        elif add:
            link = sforms.addsociallink(request.POST,request.FILES,)
            message = 'Link added'
        else:
            link = sforms.addsociallink(request.POST,request.FILES,)
            message = 'Link added'
        if link.is_valid:
            link.save()
            link = link.instance
            link.store = store
            link.save()
            message =message
            content = store_socials(request,True)
            output_data = {
            'notification': message,
            'updatecontent': content,
            'container':'store_socials_inner'

                            }
            return JsonResponse(output_data) 
        else:
            output_data = {
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        title = 'Add social link'
        if edit:
            action = 'edit'
            social = gmodels.SocialLink.objects.get(pk=id)
            allObject['social'] = social
            title = 'Edit ' + social.name
        elif add:
            action = 'add'
            title = 'Add social link'
        allObject['action'] = action

        template_name = 'seller/add_social_link.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'modal_content': content,
        'heading': title
                        }
        return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def addmeasurementunit(request, *args, **kwargs):
    edit = request.GET.get('edit')
    add = request.GET.get('add')
    id =  request.GET.get('id')
    title = 'Add measurement unit'
    action = 'add'
    if request.method == 'POST':
        if edit:
            unit = apmodels.MeasurementUnit.objects.get(pk=id)
            unit = sforms.AddMeasurementUnit(request.POST,request.FILES,instance=unit)
            message = 'Unit edited'
        elif add:
            unit = sforms.AddMeasurementUnit(request.POST,request.FILES,)
            message = 'Unit added'
        else:
            unit = sforms.AddMeasurementUnit(request.POST,request.FILES,)
            message = 'Unit added'
        if unit.is_valid:
            unit.save()
            message =message
            content = store_measurement_units(request,True)
            output_data = {
            'notification': message,
            'updatecontent': content,
            'container':'store_measurement_units_inner'

                            }
            return JsonResponse(output_data) 
        else:
            output_data = {
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        if edit:
            action = 'edit'
            unit = apmodels.MeasurementUnit.objects.get(pk=id)
            allObject['unit'] = unit
            title = 'Edit ' + unit.name
        elif add:
            action = 'add'
        allObject['action'] = action

        template_name = 'seller/add_measurement_unit.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'modal_content': content,
        'heading': title
                        }
        return JsonResponse(output_data)



@seller_login_required
@checksellerstatus
def addproductimage(request,productid=None, *args, **kwargs):
    try:
        product = apmodels.Product.objects.get(productid=productid)
    except ObjectDoesNotExist:
        output_data = {
        'notification': 'Product does not exist',
                        }
        return JsonResponse(output_data)
    allObject = inherit(request)

    if request.method == 'POST':
        product = sforms.addproductimage(request.POST,request.FILES,)
        if product.is_valid:
            product.save()
            product = product.instance
            message ='Image added'
            content = product_images(request,productid,True)
            output_data = {
            'notification': message,
            'updatecontent': content,
            'container':'product_images_inner'

                            }
            return JsonResponse(output_data) 
        else:
            output_data = {
            'modal_message': 'Could not validate',

                            }
            return JsonResponse(output_data)

    else:
        allObject = inherit(request)
        url = str(request.get_full_path())
        template_name = 'seller/add_product_image.html'
        allObject['product'] = product
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'modal_content': content,
        'heading': product.name +  ' - Add image'
                        }
        return JsonResponse(output_data)






@seller_login_required
@checksellerstatus
def select_account_type(request,*args, **kwargs):
    allObject = inherit(request)
    customer =allObject['customer'] 
    allObject['title'] = 'DPG | Account selection'
    allObject['page'] = 'Account selection'
    allObject['next'] = request.GET.get('next') or '/'
    sellertatus = checksellerstatus(request, customer)
    if customer.email_confirmed:
        pass
    elif not customer.email_confirmed and (customer.email_addres =='' or customer.email_addres =='none'):
        pass
    elif not customer.email_confirmed:
        return redirect('customer_confirm_email_page')
    else:
        pass
    # if customer.account_type_selected:
    #     if customer.profile_updated:
    #         pass
    #     else:
    #         return redirect('customer_update_profile')
    if request.method == 'POST':
        # if not customer.account_type == str(request.POST.copy().get('accounttype')):
        #     customer.photo = ''
        #     customer.profile_updated=False 
        customer.account_type=str(request.POST.copy().get('accounttype'))
        customer.account_type_selected=True

        customer.save()
        return redirect(redirect('customer_update_profile').url +'?next='+str(allObject['next'])) 

    template_name = 'seller/select_account_type.html'
    return render(request,template_name,allObject)




def cart(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/cart.html'
    # customer = allObject['customer']
    allObject['title']='Cart | '+ allObject['store'].store_name
    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            cart = apmodels.Cart.objects.get(customer = customer)
        except ObjectDoesNotExist:
            cart  = apmodels.Cart.objects.create(customer=customer)
            cart.refresh_from_db()
    else:
        try:
            cart = apmodels.Cart.objects.get(session = request.session.session_key)
        except ObjectDoesNotExist:
            cart  = apmodels.Cart.objects.create(session = request.session.session_key)
            cart.refresh_from_db()
    allObject['cart'] = cart or None

    return render(request,template_name,allObject)


@seller_login_required
@checksellerstatus
def overview(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/overview.html'
    store=allObject['store']
    products =  store.products.all()
    allObject['products']=products
    orders = list(store.orders.all())
    # neworders = list(filter(lambda x:x.seen == False,orders))
    # unpaidorders = list(filter(lambda x:x.paid == False,orders))
    paidorders = list(filter(lambda x:x.paid == True,orders))
    allObject['orders']=orders
    revenue = 0
    for order in paidorders:
            revenue+=order.amount
    allObject['revenue']='NGN '+str('{:,.2f}'.format(revenue))
    # allObject['neworders']=neworders
    # allObject['paidorders']=paidorders
    # allObject['unpaidorders']=unpaidorders
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


@seller_login_required
@checksellerstatus
def productmonthlysalesgraph(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/monthly_sales_graph.html'
    product = apmodels.Product.objects.get(productid=productid)

    orders = list(apmodels.CartedProduct.objects.filter(product=product,paid=True,date_time_paid__year = now().year))
    orders.sort(key=lambda x:x.date_time_paid.month)
    # januaryorders = len(list(filter(lambda x:x.date_time_added.month == 0,orders)))
    # for month in range(1,13):
    #     for virtorder in range(int(200 * random())):
    #         try:
    #             day = math.ceil(28 * random())
    #             newvirtual = apmodels.Order.objects.create(date_time_added = datetime.datetime(2021,month,day))
    #         except Exception:
    #             print( month,day)
    ordercount = 0  
    sales = []
    monthObj = {}
    for index in range(1,13):
        monthObj[index] = {}
        monthObj[index]['count'] =0
        for order in orders:
            if order.date_time_paid.month == index:
                monthObj[index]['count']+=order.quantity
                
        sales.append(monthObj[index]['count'])
        # else:
        #     sales.append(order)
        #     ordercount = 0
            # index = order.date_time_added.month
    # for order in orders:
    #     if order.date_time_added.month == index:
    #         ordercount+=1
    #     else:
    #         sales.append(ordercount)
    #         index = order.date_time_added.month
    # sales.append(januaryorders)
    print(sales)
    allObject['sales']=sales
    allObject['year']=now().year
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
    'title':'Monthly graph'
                    }
    return JsonResponse(output_data) 


@seller_login_required
@checksellerstatus
def product_overview(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/product_overview.html'
    product = apmodels.Product.objects.get(productid=productid)
    revenue = 0
    orders = apmodels.CartedProduct.objects.filter(product=product,paid=True)
    for order in orders:
        revenue+=order.amount
    sales = product.purchase_count
    seen = product.view_count
    allObject['sales']=sales
    allObject['product']=product
    allObject['seen']=seen
    allObject['revenue']='NGN '+str('{:,.2f}'.format(revenue))
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


@seller_login_required
@checksellerstatus
def product_information(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/product_information.html'
    product = apmodels.Product.objects.get(productid=productid)

    allObject['product']=product
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

@seller_login_required
@checksellerstatus
def product_images(request,productid=None,inline=False, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/product_images.html'
    product = apmodels.Product.objects.get(productid=productid)
    images = apmodels.ProductImage.objects.filter(product=product)
    # for image in images:
    #     image.save()
    allObject['product']=product
    allObject['images']=images
    content = loader.render_to_string(template_name,allObject,request)
    if inline:
        return content
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 



@seller_login_required
@checksellerstatus
def product_variations(request,productid=None,inline=False, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/product_variations.html'
    product = apmodels.Product.objects.get(productid=productid)
    variations = product.variations.all()
    # for image in images:
    #     image.save()
    allObject['product']=product
    allObject['variations']=variations
    content = loader.render_to_string(template_name,allObject,request)
    if inline:
        return content
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 



@seller_login_required
@checksellerstatus
def orders(request,filters=None, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/orders.html'
    store = allObject['store']
    orders = list(store.orders.all())
    if filters == 'all':
        orders = orders
        page='All orders'
        title='All orders - ' + allObject['store'].store_name
    elif filters == 'new':
        orders = list(filter(lambda x:x.seen == False,orders))
        page='New orders'
        title='New orders  - ' + allObject['store'].store_name

    elif filters =='paid':
        orders = list(filter(lambda x:x.paid == True,orders))
        page ='Paid orders'
        title='Paid orders - ' + allObject['store'].store_name

    elif filters == 'unpaid':
        orders = list(filter(lambda x:x.paid == False,orders))
        page ='Unpaid orders'
        title='Unpaid orders - ' + allObject['store'].store_name

    # for order in orders:
    #     order.save()
    orders.sort(key=lambda x:x.date_time_added)
    # for virtualorder in range(1,13):
    #     for count in range(int(100*random())):
    #         apmodels.Order.objects.create(date_time_added=datetime.datetime(2021,virtualorder,math.ceil(28*random())))
    reqpage = request.GET.get('page', 1)

    paginator = Paginator(orders, 9)
    try:
        paginated = paginator.page(reqpage)
    except PageNotAnInteger:
        paginated = paginator.page(1)
    except EmptyPage:
        paginated = paginator.page(paginator.num_pages)
    allObject['orders']=paginated
    allObject['section'] = 'orders'
    allObject['paginated'] = str(request.path)
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
    'title':title,
    'page':page
                    }
    return JsonResponse(output_data) 



@seller_login_required
@checksellerstatus
def products(request,filter=None, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/products.html'
    store=allObject['store']
    allproducts =  list(store.products.all())
    allObject['products']=allproducts
    page='Products'
 
    allproducts.sort(key=lambda x:x.date_time_added)
    # for virtualorder in range(1,13):
    #     for count in range(int(100*random())):
    #         apmodels.Order.objects.create(date_time_added=datetime.datetime(2021,virtualorder,math.ceil(28*random())))
    reqpage = request.GET.get('page', 1)

    paginator = Paginator(allproducts, 9)
    try:
        paginated = paginator.page(reqpage)
    except PageNotAnInteger:
        paginated = paginator.page(1)
    except EmptyPage:
        paginated = paginator.page(paginator.num_pages)
    allObject['products']=paginated
    allObject['section'] = 'products'
    allObject['paginated'] = str(request.path)
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
    'title':'Products - '+allObject['store'].store_name,
    'page':page
                    }
    return JsonResponse(output_data) 



@seller_login_required
@checksellerstatus
def neworders(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/orders.html'
    orders = list(apmodels.Order.objects.filter(seen = False))
    # for order in orders:
    #     order.save()
    orders.sort(key=lambda x:x.date_time_added)
    # for virtualorder in range(1,13):
    #     for count in range(int(100*random())):
    #         apmodels.Order.objects.create(date_time_added=datetime.datetime(2021,virtualorder,math.ceil(28*random())))
    page = request.GET.get('page', 1)

    paginator = Paginator(orders, 9)
    try:
        paginated = paginator.page(page)
    except PageNotAnInteger:
        paginated = paginator.page(1)
    except EmptyPage:
        paginated = paginator.page(paginator.num_pages)
    allObject['orders']=paginated
    allObject['section'] = 'orders'
    allObject['paginated'] = str(request.path)
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


@seller_login_required
@checksellerstatus
def order(request,orderid=None, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/order.html'
    order = apmodels.CartedProduct.objects.get(cartedproductid=orderid)
    allObject['order']=order
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


@seller_login_required
@checksellerstatus
def product(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/product.html'
    product = apmodels.Product.objects.get(productid=productid)
    allObject['product']=product
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


@seller_login_required
@checksellerstatus
def orderspage(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/orders_page.html'
    orders = list(apmodels.Order.objects.filter(date_time_added__year = now().year))[0:9]
    orders.sort(key=lambda x:x.date_time_added)
    allObject['orders']=orders
    content = loader.render_to_string(template_name,allObject,request)

    output_data = {
    'content': content,
    'title':'Orders - ' + allObject['store'].store_name
                    }
    return JsonResponse(output_data) 



@seller_login_required
@checksellerstatus
def productspage(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/products_page.html'
    content = loader.render_to_string(template_name,allObject,request)

    output_data = {
    'content': content,
    'title':'Products - ' + allObject['store'].store_name,
    'page':'Products'
                    }
    return JsonResponse(output_data) 


@seller_login_required
@checksellerstatus
def allproducts(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/products.html'
    store=allObject['store']
    products =  store.products.all()
    allObject['products']=products
    products.sort(key=lambda x:x.date_time_added,reverse=True)
    # for virtualorder in range(1,13):
    #     for count in range(int(100*random())):
    #         apmodels.Order.objects.create(date_time_added=datetime.datetime(2021,virtualorder,math.ceil(28*random())))

    allObject['products']=products
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

@seller_login_required
@checksellerstatus
def monthlysalesgraph(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/monthly_sales_graph.html'
    store = allObject['store']
    orders = list(store.orders.all())
    
    orders = list(filter(lambda x:x.date_time_added.year == now().year and x.ordered==True,orders))
    orders.sort(key=lambda x:x.date_time_added.month)
    # for month in range(1,13):
    #     for virtorder in range(int(200 * random())):
    #         try:
    #             day = math.ceil(28 * random())
    #             newvirtual = apmodels.Order.objects.create(date_time_added = datetime.datetime(2021,month,day))
    #         except Exception:
    #             print( month,day)
    sales = []
    monthObj = {}
    for index in range(1,13):
        monthObj[index] = {}
        monthObj[index]['count'] =0
        for order in orders:
            if order.date_time_added.month == index:   
                monthObj[index]['count']+=order.quantity
                
        sales.append(monthObj[index]['count'])
        # else:
        #     sales.append(order)
        #     ordercount = 0
            # index = order.date_time_added.month
    # for order in orders:
    #     if order.date_time_added.month == index:
    #         ordercount+=1
    #     else:
    #         sales.append(ordercount)
    #         index = order.date_time_added.month
    # sales.append(januaryorders)
    allObject['sales']=sales
    allObject['year']=now().year
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
    'title':'Monthly graph'
                    }
    return JsonResponse(output_data) 




@seller_login_required
@checksellerstatus
def updatecontactdetails(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/cart.html'
    allObject['title']='Update contact details | '+ allObject['store'].store_name
    customer = allObject['customer']
    if request.method == 'POST':
        customerform = cforms.updatecontactdetails(request.POST,instance=customer)
        if customerform.is_valid():
            customerform.save()
            customer.contact_ready = True
            customer.save()
        allObject['message'] = '<span class="text-primary uk-text-bold h1">Contact details updated.</span>'
        message_template = 'general/success.html'
        # global message
        message = loader.render_to_string(message_template,allObject,request)
        output_data = {
        'modal_message': message,
                        }
        return JsonResponse(output_data) 
    else:
        pass

    return render(request,template_name,allObject)




def search_products(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/search_result.html'
    if request.method == 'POST':
        query = request.POST.copy().get('query')
        products = apmodels.Product.objects.all()
        search_result = []
        for product in products:
            if query.lower() in str(product.name).lower():
                search_result.append(product)
        allObject['products'] = search_result
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'content': content,
                        }
        return JsonResponse(output_data) 



def remove_order(request,id=None, *args, **kwargs):
    allObject = inherit(request)
    customer = False
    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            order = apmodels.Order.objects.get(customer = customer,orderid=id)
        except ObjectDoesNotExist:
            pass
        
    else:
        try:
            order = apmodels.Order.objects.get(session = request.session.session_key,orderid=id)

        except ObjectDoesNotExist:
            pass

    order.deleted = True
    order.save() 
    subject = 'Order Cancelled - '+id

    message = render_to_string('seller/order_cancelled.html', {
            'order':order,
            'title':'ORDER CANCELED',
            'socials':gmodels.SocialLink.objects.all(),
            'store':allObject['store']
            })
    recipient_list = [allObject['store'].email, ]
    to = recipient_list
    subject = subject
    body = message
    sendmail(to,body,body,subject)
    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            orders = apmodels.Order.objects.filter(customer = customer,deleted=False)
        except ObjectDoesNotExist:
            pass
        
    else:
        try:
            orders = apmodels.Order.objects.filter(session = request.session.session_key,deleted=False)

        except ObjectDoesNotExist:
            pass
       
    allObject['orders'] = orders
    content_template = 'seller/order_container.html'
    content = loader.render_to_string(content_template,allObject,request)

    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

def myorders(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/my_orders.html'
    # customer = allObject['customer']
    allObject['title']='My orders | '+ allObject['store'].store_name
    if request.user.is_authenticated:
        customer = allObject['customer']
        orders = apmodels.Order.objects.filter(customer = customer,deleted=False)
    else:
        try:
            orders = apmodels.Order.objects.filter(session = request.session.session_key,deleted=False)
        except ObjectDoesNotExist:
            orders = None
    allObject['orders'] = orders or None

    return render(request,template_name,allObject)


def allproductspage(request, *args, **kwargs):
    allObject = inherit(request)
    

    logrequest(request,'')

    template_name = 'seller/all_products.html'
    # customer = allObject['customer']
    allObject['title']='All products | '+ allObject['store'].store_name

    return render(request,template_name,allObject)


@seller_login_required
@checksellerstatus

def categorys(request,name=None, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/category_page.html'
    # customer = allObject['customer']
    category = apmodels.Category.objects.get(name=name)

    allObject['title']='Categories . '+ allObject['store'].store_name
    allObject['category']=category

    return render(request,template_name,allObject)



def slideshowpage(request,slug=None, *args, **kwargs):
    allObject = inherit(request)
    

    logrequest(request,'')

    template_name = 'seller/slideshow_page.html'
    # customer = allObject['customer']
    slideshow = apmodels.SlideShow.objects.get(slug=slug)

    allObject['title']=slideshow.name+ ' '+ allObject['store'].store_name
    allObject['slideshow']=slideshow

    return render(request,template_name,allObject)


def slideshowproducts(request,slug=None, *args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    slideshow = apmodels.SlideShow.objects.get(slug=slug)
    products = list(slideshow.products.all())
    products.sort(key=lambda x:x.date_time_added,reverse=True)
    # for product in products:
    #     product.save()
    allObject['products'] = products
    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 



def brandpage(request,slug=None, *args, **kwargs):
    

    logrequest(request,'')

    allObject = inherit(request)
    template_name = 'seller/brand_page.html'
    # customer = allObject['customer']
    brand = apmodels.Brand.objects.get(slug=slug)

    allObject['title']=brand.name+ ' '+ allObject['store'].store_name
    allObject['brand']=brand

    return render(request,template_name,allObject)


def brandproducts(request,slug=None, *args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    brand = apmodels.Brand.objects.get(slug=slug)
    products = list(brand.products.all())
    products.sort(key=lambda x:x.date_time_added,reverse=True)
    # for product in products:
    #     product.save()
    allObject['products'] = products
    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def flashsalespage(request,id=None, *args, **kwargs):
    

    logrequest(request,'')

    allObject = inherit(request)
    template_name = 'seller/flash_sales_page.html'
    # customer = allObject['customer']
    flashsale = apmodels.FlashSale.objects.get(id=id)

    allObject['title']='Flashsale . '+ allObject['store'].store_name
    allObject['flashsale']=flashsale

    return render(request,template_name,allObject)


def homegroup(request,slug=None, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/home_group_page.html'
    # customer = allObject['customer']
    home_group = apmodels.HomePageGroup.objects.get(slug=slug)

    allObject['title']=home_group.name+' '+ allObject['store'].store_name
    allObject['homegroup']=home_group
    allObject['section'] =home_group.slug

    return render(request,template_name,allObject)


def saveditemspage(request,slug=None, *args, **kwargs):
    

    logrequest(request,'')

    allObject = inherit(request)
    template_name = 'seller/saved_items_page.html'
    # customer = allObject['customer']

    allObject['title']='Saved Items . '+ allObject['store'].store_name

    return render(request,template_name,allObject)


def savedproducts(request, *args, **kwargs):
    allObject = inherit(request)
    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            saved = apmodels.Saved.objects.get(customer = customer)
        except ObjectDoesNotExist:
            saved  = apmodels.Saved.objects.create(customer=customer)
            saved.refresh_from_db()
    else:
        try:
            saved = apmodels.Saved.objects.get(session = request.session.session_key)
        except ObjectDoesNotExist:
            saved  = apmodels.Saved.objects.create(session = request.session.session_key)
            saved.refresh_from_db()
    allObject['saved'] = saved or None
    saved_products = saved.products.all()
    allObject['products'] = saved_products
    allObject['paginatedproducts'] = str(request.path)
    allObject['session'] ='saved-items'

    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def categoryproducts(request,name=None, *args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    category = apmodels.Category.objects.get(name=name)
    products = list(category.products.all())
    products.sort(key=lambda x:x.date_time_added,reverse=True)
    # for product in products:
    #     product.save()
    allObject['products'] = products[0:12]
    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def homegrouppage(request,slug=None, *args, **kwargs):
    

    logrequest(request,'')

    allObject = inherit(request)
    homegroup = apmodels.HomePageGroup.objects.get(slug=slug)
    products = list(homegroup.products.all())
    products.sort(key=lambda x:x.date_time_added,reverse=True)
    allObject['products'] = products
    allObject['section'] =homegroup.slug
    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

@seller_login_required
@checksellerstatus
def product_details(request,productid=None,inline=False, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/product_details.html'
    product = apmodels.Product.objects.get(productid=productid)
    product.save()
    allObject['year']=now().year

    productimages = apmodels.ProductImage.objects.filter(product=product)
    allObject['productimages'] = productimages
    flashsales = apmodels.FlashSale.objects.filter(end_date_time__gte =now(),start_date_time__lte=now())
    for flashsale in flashsales:
        for flashsaleproduct in flashsale.products.all():
            if product == flashsaleproduct.product:
                allObject['flashsaleproduct'] = flashsaleproduct
                break
    # customer = allObject['customer']
    allObject['title']= product.name + ' | ' +allObject['store'].store_name
    allObject['page'] = 'Product'
    allObject['product'] = product
    variations = list(product.variations.all())
    variations.sort(key=lambda x:x.price,reverse=False)
    if variations:
        allObject['variations'] =variations[0]
    slideshows = apmodels.SlideShow.objects.all()
    allObject['slideshows'] = slideshows
    content = loader.render_to_string(template_name,allObject,request)
    if inline:
        return content
    output_data = {
    'content': content,
    'title': product.name + " - " + allObject['store'].store_name,
    'page':product.name
                    }
    return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def order_details(request,orderid=None,inline=False, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/order_details.html'
    order = apmodels.Order.objects.get(orderid=orderid)
    order.seen = True
    order.save()
    allObject['year']=now().year
    allObject['title']= order.orderid + ' | ' +allObject['store'].store_name
    allObject['page'] = 'Order'
    allObject['order'] = order
    allObject['customer'] = order.customer
    content = loader.render_to_string(template_name,allObject,request)
    if inline:
        return content
    output_data = {
    'content': content,
    'title': 'Order - '+ order.orderid + " - " + allObject['store'].store_name,
    'page':'Order - '+order.orderid
                    }
    return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def settings(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/settings.html'

    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'content': content,
    'page':'Store settings',
    'title':'Settings - ' +allObject['store'].store_name
                    }
    return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def store_information(request,inline=False, *args, **kwargs):
    allObject = inherit(request)

    template_name = 'seller/store_information.html'
    store = allObject['store']

    allObject['store']=store
    content = loader.render_to_string(template_name,allObject,request)
    if inline:
        return content
    output_data = {
    'content': content,
    'title':'Store information | ' + allObject['store'].store_name,
    'page':'Store information'
                    }
    return JsonResponse(output_data) 

@seller_login_required
@checksellerstatus
def store_payment(request,inline=False, *args, **kwargs):
    allObject = inherit(request)

    template_name = 'seller/store_payment.html'
    store = allObject['store']

    allObject['store']=store
    content = loader.render_to_string(template_name,allObject,request)
    if inline:
        return content
    output_data = {
    'content': content,
    'title':'Store payment | ' + allObject['store'].store_name,
    'page':'Store payment'
                    }
    return JsonResponse(output_data) 

@seller_login_required
@checksellerstatus
def store_branding(request,inline=False, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/store_branding.html'
    store = allObject['store']

    allObject['store']=store
    content = loader.render_to_string(template_name,allObject,request)
    if inline:
        return content
    output_data = {
    'content': content,
    'title':'Store branding | ' + allObject['store'].store_name,
    'page':'Store branding'
                    }
    return JsonResponse(output_data) 


@seller_login_required
@checksellerstatus
def store_socials(request,inline=False, *args, **kwargs):
    allObject = inherit(request)

    template_name = 'seller/store_social_media_platforms.html'
    socials = allObject['store'].social_links.all()

    allObject['socials']=socials
    content = loader.render_to_string(template_name,allObject,request)
    if inline:
        return content
    output_data = {
    'content': content,
    'title':'Store social platforms | ' + allObject['store'].store_name,
    'page':'Store social platforms'
                    }
    return JsonResponse(output_data) 



@seller_login_required
@checksellerstatus
def store_measurement_units(request,inline=False, *args, **kwargs):
    allObject = inherit(request)

    template_name = 'seller/store_measurement_units.html'
    content = loader.render_to_string(template_name,allObject,request)
    if inline:
        return content
    output_data = {
    'content': content,
    'title':'Store measurement units | ' + allObject['store'].store_name,
    'page':'Store measurement units'
                    }
    return JsonResponse(output_data) 


def cart_count(request, *args, **kwargs):
    allObject = inherit(request)
    if request.user.is_authenticated:
        if request.user.is_superuser:

            try:
                cart = apmodels.Cart.objects.get(session = request.session.session_key)
                cart_products_count = cart.products.all().count()
            except ObjectDoesNotExist:
                cart_products_count = 0
        else:
            customer = allObject['customer']
            try:
                cart = apmodels.Cart.objects.get(customer = customer)
                cart_products_count = cart.products.all().count()
            except ObjectDoesNotExist:
                cart_products_count=0
    else:
        try:
            cart = apmodels.Cart.objects.get(session = request.session.session_key)
            cart_products_count = cart.products.all().count()
        except ObjectDoesNotExist:
            cart_products_count = 0

    cart_products_count = cart_products_count or 0

    output_data = {
    'content': str(cart_products_count)
                    }
    return JsonResponse(output_data)




def allhomegroupsection(request,*args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    homegroups = list(apmodels.HomePageGroup.objects.all())
    homegroups.sort(key=lambda x: x.index)
    allObject['homegroups'] = homegroups
    content_template = 'seller/home_group_container.html'
    allObject['section'] = 'home-group-sections'
    allObject['paginatedproducts'] = str(request.path)
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 



def products_you_may_like(request,*args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    allproducts = list(apmodels.Product.objects.all())[:10]
    allproducts.sort(key=lambda x:x.purchase_count,reverse=True)
    page = request.GET.get('page', 1)

    paginator = Paginator(allproducts, 10)
    try:
        pagproducts = paginator.page(page)
    except PageNotAnInteger:
        pagproducts = paginator.page(1)
    except EmptyPage:
        pagproducts = paginator.page(paginator.num_pages)
    allObject['products'] = pagproducts
    content_template = 'seller/products.html'
    allObject['section'] = 'products-you-may-like'
    allObject['paginatedproducts'] = str(request.path)
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 



def similarproducts(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    product = apmodels.Product.objects.get(productid=productid)
    tags = product.tags.all()
    similar_products = apmodels.Product.objects.filter(tags__in=tags).distinct().exclude(productid=product.productid)

    # for product in products:
  
    allObject['products'] = similar_products
    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

def allproducts(request, *args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    store=allObject['store']
    allproducts =  store.products.all()
    allObject['products']=allproducts
    allproducts.sort(key=lambda x:x.purchase_count,reverse=True)
    # for product in products:
    #     product.save()
    page = request.GET.get('page', 1)

    paginator = Paginator(allproducts, 10)
    try:
        pagproducts = paginator.page(page)
    except PageNotAnInteger:
        pagproducts = paginator.page(1)
    except EmptyPage:
        pagproducts = paginator.page(paginator.num_pages)
    allObject['products'] = pagproducts
    allObject['paginatedproducts'] = str(request.path)
    allObject['section']='all-products'
    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def homegroupproducts(request,id=None, *args, **kwargs):
    allObject = inherit(request)
    home_group = apmodels.HomePageGroup.objects.get(pk=id)
    # for product in products:
    #     product.save()
    allproducts = home_group.products.all()[:10]

    page = request.GET.get('page', 1)

    paginator = Paginator(allproducts, 10)
    try:
        pagproducts = paginator.page(page)
    except PageNotAnInteger:
        pagproducts = paginator.page(1)
    except EmptyPage:
        pagproducts = paginator.page(paginator.num_pages)
    allObject['products'] = pagproducts
    allObject['paginatedproducts'] = str(request.path)
    allObject['section'] =home_group.slug

    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 



def allhomegroupproducts(request,slug=None, *args, **kwargs):
    allObject = inherit(request)
    home_group = apmodels.HomePageGroup.objects.get(slug=slug)
    # for product in products:
    #     product.save()
    allproducts = home_group.products.all()

    page = request.GET.get('page', 1)

    paginator = Paginator(allproducts, 10)
    try:
        pagproducts = paginator.page(page)
    except PageNotAnInteger:
        pagproducts = paginator.page(1)
    except EmptyPage:
        pagproducts = paginator.page(paginator.num_pages)
    allObject['products'] = pagproducts
    allObject['paginatedproducts'] = str(request.path)
    allObject['section'] =home_group.slug

    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def newproducts(request,*args, **kwargs):
    allObject = inherit(request)
    allproducts = list(apmodels.Product.objects.all())
    # for product in products:
    #     product.save()
    allproducts.sort(key=lambda x:x.date_time_added,reverse=True)
    new_products = allproducts[:5]
    page = request.GET.get('page', 1)

    paginator = Paginator(new_products, 10)
    try:
        pagproducts = paginator.page(page)
    except PageNotAnInteger:
        pagproducts = paginator.page(1)
    except EmptyPage:
        pagproducts = paginator.page(paginator.num_pages)
    allObject['products'] = pagproducts
    allObject['paginatedproducts'] = str(request.path)
    allObject['section'] = 'new-products'

    content_template = 'seller/new_products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def allflashsaleproducts(request,id=None, *args, **kwargs):
    allObject = inherit(request)
    allproducts = apmodels.FlashSale.objects.get(pk=id).products.all()
    # for product in products:
    #     product.save()

    page = request.GET.get('page', 1)

    paginator = Paginator(allproducts, 10)
    try:
        pagproducts = paginator.page(page)
    except PageNotAnInteger:
        pagproducts = paginator.page(1)
    except EmptyPage:
        pagproducts = paginator.page(paginator.num_pages)
    allObject['products'] = pagproducts
    allObject['paginatedproducts'] = str(request.path)

    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

def flashsaleproducts(request,id=None, *args, **kwargs):
    allObject = inherit(request)
    allproducts = apmodels.FlashSale.objects.get(pk=id).products.all()[:6]
    # for product in products:
    #     product.save()

    page = request.GET.get('page', 1)

    paginator = Paginator(allproducts, 10)
    try:
        pagproducts = paginator.page(page)
    except PageNotAnInteger:
        pagproducts = paginator.page(1)
    except EmptyPage:
        pagproducts = paginator.page(paginator.num_pages)
    allObject['products'] = pagproducts
    allObject['paginatedproducts'] = str(request.path)

    content_template = 'seller/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def flashsaleproduct(request,id=None, *args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    product = apmodels.FlashSaleProduct.objects.get(pk=id)
    productimages = apmodels.ProductImage.objects.filter(product=product.product)
    allObject['productimages'] = productimages
    allObject['product'] = product
    content_template = 'seller/flash_sale_product.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


# def product(request,id=None, *args, **kwargs):
#     allObject = inherit(request)
#     # customer = allObject['customer']
#     if request.user.is_authenticated:
#         if request.user.is_superuser:
#             pass
#         else:
#             customer = allObject['customer']
#             try:
#                     saved = apmodels.Saved.objects.get(customer = customer,)
#                     allObject['saved'] = saved
#             except ObjectDoesNotExist:
#                 pass
#     else:

#         try:
#             saved = apmodels.Saved.objects.get(session = request.session.session_key,)
#             allObject['saved'] = saved
#         except ObjectDoesNotExist:
#             pass
#     product = apmodels.Product.objects.get(pk=id)
#     productimages = apmodels.ProductImage.objects.filter(product=product,flip=True)
#     try:
#         allObject['flipimage'] = productimages[0]
#     except Exception:
#         pass
#     allObject['product'] = product
#     content_template = 'seller/product.html'
#     content = loader.render_to_string(content_template,allObject,request)
#     output_data = {
#     'content': content,
#                     }
#     return JsonResponse(output_data) 


def cartedproduct(request,id=None, *args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    cartedproduct = apmodels.CartedProduct.objects.get(cartedproductid=id)
    flashsales = apmodels.FlashSale.objects.filter(end_date_time__gte =now(),start_date_time__lte=now())
    for flashsale in flashsales:
        for flashsaleproduct in flashsale.products.all():
            if cartedproduct.product == flashsaleproduct.product:
                allObject['flashsaleproduct'] = flashsaleproduct
                break

    allObject['product'] = cartedproduct
    content_template = 'seller/carted_product.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def slideshows(request,*args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    allslideshows = list(apmodels.SlideShow.objects.all())
    # for product in products:
    #     product.save()

    allObject['slideshows'] = allslideshows
    content_template = 'seller/slideshows.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

def paginatedproducts(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']
    allproducts = list(apmodels.Product.objects.all())
    allproducts.sort(key=lambda x:x.purchase_count,reverse=True)
    # for product in products:
    #     product.save()
    page = request.GET.get('page', 1)

    paginator = Paginator(allproducts, 10)
    try:
        pagproducts = paginator.page(page)
    except PageNotAnInteger:
        pagproducts = paginator.page(1)
    except EmptyPage:
        pagproducts = paginator.page(paginator.num_pages)
    allObject['products'] = pagproducts
    allObject['paginatedproducts'] = str(request.path)

    content_template = 'seller/paginated_products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def place_order(request,*args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']
    if request.method == 'POST':
        delivery = str(request.POST.copy().get('delivery'))
        location = str(request.POST.copy().get('location'))
        if delivery != 'p':
            if customer.contact_ready:
                pass
            else:
                content_template = 'seller/contact_form.html'
                content = loader.render_to_string(content_template,allObject,request)
                url = str(request.get_full_path())
                next = redirect('customer_update_contact_details').url  +'?next='+url
                allObject['next'] = next
                output_data = {
                'modal_message':content,
                'next': next,
                                }
                return JsonResponse(output_data) 
                # product = apmodels.Product.objects.get(productid=productid)
        if request.user.is_authenticated:
            customer = allObject['customer']
            try:
                cart = apmodels.Cart.objects.get(customer = customer)
            except ObjectDoesNotExist:
                cart  = apmodels.Cart.objects.create(customer=customer)
                cart.refresh_from_db()
            if len(cart.products.all()) < 1:

                output_data = {
                'modal_message': "<span class='text-danger text-bold'> No Product in cart </span>",
                                }
                return JsonResponse(output_data)            
            order = apmodels.Order.objects.create(customer=customer)

        else:
                    try:
                        cart = apmodels.Cart.objects.get(session = request.session.session_key)

                    except ObjectDoesNotExist:
                        cart  = apmodels.Cart.objects.create(session=request.session.session_key)
                        cart.refresh_from_db()
                    if len(cart.products.all()) < 1:

                        output_data = {
                        'modal_message': "<span class='text-danger text-bold'> No Product in cart </span>",
                                        }
                        return JsonResponse(output_data)         
                    order = apmodels.Order.objects.create(session=request.session.session_key)
            
        order.refresh_from_db()
        for product in cart.products.all():
            order.products.add(product)
        
        if delivery == 'p':
            order.delivery_option=delivery
        elif delivery == 'd':
            order.delivery_option=delivery
            location = apmodels.DeliveryLocation.objects.get(pk=int(location))
            order.delivery_location = location
        order.save()

        # except ObjectDoesNotExist:
        #     cartedproduct = apmodels.CartedProduct.objects.create(product=product, session=request.session.session_key,quantity = quantity)
        #     cart.products.add(cartedproduct)
        cart.products.clear()
        allObject['order'] = order
        content_template = 'seller/order_placed.html'
        content = loader.render_to_string(content_template,allObject,request)
        output_data = {
        'modal_message': content,
                        }
        return JsonResponse(output_data) 

        

def newlettersubscription(request, *args, **kwargs):
    if request.method == 'POST':
        email = str(request.POST.copy().get('email'))

        try:
            subscription = apmodels.NewsLetterSubscription.objects.get(email = email)

        except ObjectDoesNotExist:
            subscription  = apmodels.NewsLetterSubscription.objects.create(email=email)
    output_data = {
    'notification': 'You have been subscribed to our news letter',
                    }
    return JsonResponse(output_data) 


def update_cart(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    # customer = allObject['customer']

    if request.method == 'POST':
        productid = str(request.POST.copy().get('productid'))
        quantity = int(request.POST.copy().get('quantity'))
        # product = apmodels.Product.objects.get(productid=productid)
    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            cart = apmodels.Cart.objects.get(customer = customer)
        except ObjectDoesNotExist:
            pass
    else:
        try:
            cart = apmodels.Cart.objects.get(session = request.session.session_key)

        except ObjectDoesNotExist:
            cart  = apmodels.Cart.objects.create(session=request.session.session_key)
            cart.refresh_from_db()
    for product in cart.products.all():
        if product.cartedproductid == productid:
            cartedproduct = product
            cartedproduct.quantity = quantity
            cartedproduct.save()
            break
    # except ObjectDoesNotExist:
    #     cartedproduct = apmodels.CartedProduct.objects.create(product=product, session=request.session.session_key,quantity = quantity)
    #     cart.products.add(cartedproduct)
    cart.save()
    allObject['message'] = 'Product updated'
    message_template = 'general/success.html'
    global message
    message = loader.render_to_string(message_template,allObject,request)
    cart.refresh_from_db()

    output_data = {
    'success_alert': 'Product updated',
                    }
    return JsonResponse(output_data) 

def add_to_cart(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    customer = False

    if request.method == 'POST':
        productid = str(request.POST.copy().get('productid'))
        variationid = str(request.POST.copy().get('variation'))
        quantity = int(request.POST.copy().get('quantity'))
        product = apmodels.Product.objects.get(productid=productid)
        try:
            variationid =int(variationid)
        except ValueError:
            variationid = ''
        if product.variations.all():
            productvariation = apmodels.ProductVariation.objects.get(id=variationid)

        if request.user.is_authenticated:
            customer = allObject['customer']
            try:
                cart = apmodels.Cart.objects.get(customer = customer)
            except ObjectDoesNotExist:
                cart  = apmodels.Cart.objects.create(customer=customer)
                cart.refresh_from_db()
            try:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,ordered=False, variation__id=variationid, customer=customer)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,ordered=False, customer=customer)

            except ObjectDoesNotExist:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product,variation=productvariation or None, customer=customer,quantity = quantity)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product, customer=customer,quantity = quantity)
        
        else:
            try:
                cart = apmodels.Cart.objects.get(session = request.session.session_key)

            except ObjectDoesNotExist:
                cart  = apmodels.Cart.objects.create(session=request.session.session_key)
                cart.refresh_from_db()
            try:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,variation__id=variationid, session = request.session.session_key)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product, session = request.session.session_key)

            except ObjectDoesNotExist:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product,variation=productvariation or None, session=request.session.session_key,quantity = quantity)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product, session=request.session.session_key,quantity = quantity)

        cartedproduct.quantity = quantity
        cartedproduct.save()        
        cart.products.add(cartedproduct)

        allObject['message'] = '<span class="text-primary uk-text-bold h1">Product added to cart </span>'
        message_template = 'general/success.html'
        global message
        cart.refresh_from_db()

        output_data = {
        'content': cart.products.all().count(),
        'modal_message': 'Product added to cart',
                        }
        return JsonResponse(output_data) 
    else:
        product = apmodels.Product.objects.get(productid=productid)
        allObject['product'] = product
        if product.variations.all():

            variations = list(product.variations.all())
            variations.sort(key=lambda x:x.price,reverse=False)
            if variations:

                allObject['cheapestvariations'] =variations[0]
                allObject['variations'] = variations
                flashsales = apmodels.FlashSale.objects.filter(end_date_time__gte =now(),start_date_time__lte=now())
                for flashsale in flashsales:
                    for flashsaleproduct in flashsale.products.all():
                        if product == flashsaleproduct.product:
                            allObject['flashsaleproduct'] = flashsaleproduct
                            break
                content_template = 'seller/cart_form_modal.html'
                content = loader.render_to_string(content_template,allObject,request)
                output_data = {
                'modal_message': content,
                                }
                return JsonResponse(output_data) 

        else:
            if request.user.is_authenticated:
                customer = allObject['customer']
                try:
                    cart = apmodels.Cart.objects.get(customer = customer)
                except ObjectDoesNotExist:
                    cart  = apmodels.Cart.objects.create(customer=customer)
                    cart.refresh_from_db()
                try:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product, customer=customer)

                except ObjectDoesNotExist:

                    cartedproduct = apmodels.CartedProduct.objects.create(product=product, customer=customer,quantity = 1)
            
            else:
                try:
                    cart = apmodels.Cart.objects.get(session = request.session.session_key)

                except ObjectDoesNotExist:
                    cart  = apmodels.Cart.objects.create(session=request.session.session_key)
                    cart.refresh_from_db()
                try:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product, session = request.session.session_key)

                except ObjectDoesNotExist:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product, session=request.session.session_key,quantity = 1)

            cartedproduct.quantity = 1
            cartedproduct.save()        
            cart.products.add(cartedproduct)
            output_data = {
            'notification': 'Product added to cart',
            'loadcontent':True,
            'reload_url':redirect('customer_cart_count').url,
            'container':'cart-count'
                            }
            return JsonResponse(output_data)


def add_to_cart(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    customer = False

    if request.method == 'POST':
        productid = str(request.POST.copy().get('productid'))
        variationid = str(request.POST.copy().get('variation'))
        quantity = int(request.POST.copy().get('quantity'))
        product = apmodels.Product.objects.get(productid=productid)
        try:
            variationid =int(variationid)
        except ValueError:
            variationid = ''
        if product.variations.all():
            productvariation = apmodels.ProductVariation.objects.get(id=variationid)

        if request.user.is_authenticated:
            customer = allObject['customer']
            try:
                cart = apmodels.Cart.objects.get(customer = customer)
            except ObjectDoesNotExist:
                cart  = apmodels.Cart.objects.create(customer=customer)
                cart.refresh_from_db()
            try:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,variation__id=variationid, customer=customer)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product, customer=customer)

            except ObjectDoesNotExist:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product,variation=productvariation or None, customer=customer,quantity = quantity)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product, customer=customer,quantity = quantity)
        
        else:
            try:
                cart = apmodels.Cart.objects.get(session = request.session.session_key)

            except ObjectDoesNotExist:
                cart  = apmodels.Cart.objects.create(session=request.session.session_key)
                cart.refresh_from_db()
            try:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,variation__id=variationid, session = request.session.session_key)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product, session = request.session.session_key)

            except ObjectDoesNotExist:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product,variation=productvariation or None, session=request.session.session_key,quantity = quantity)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product, session=request.session.session_key,quantity = quantity)

        cartedproduct.quantity = quantity
        cartedproduct.save()        
        cart.products.add(cartedproduct)

        allObject['message'] = '<span class="text-primary uk-text-bold h1">Product added to cart </span>'
        message_template = 'general/success.html'
        global message
        cart.refresh_from_db()

        output_data = {
        'content': cart.products.all().count(),
        'modal_message': 'Product added to cart',
                        }
        return JsonResponse(output_data) 
    else:
        product = apmodels.Product.objects.get(productid=productid)
        allObject['product'] = product
        if product.variations.all():

            variations = list(product.variations.all())
            variations.sort(key=lambda x:x.price,reverse=False)
            if variations:

                allObject['cheapestvariations'] =variations[0]
                allObject['variations'] = variations
                flashsales = apmodels.FlashSale.objects.filter(end_date_time__gte =now(),start_date_time__lte=now())
                for flashsale in flashsales:
                    for flashsaleproduct in flashsale.products.all():
                        if product == flashsaleproduct.product:
                            allObject['flashsaleproduct'] = flashsaleproduct
                            break
                content_template = 'seller/cart_form_modal.html'
                content = loader.render_to_string(content_template,allObject,request)
                output_data = {
                'modal_message': content,
                                }
                return JsonResponse(output_data) 

        else:
            if request.user.is_authenticated:
                customer = allObject['customer']
                try:
                    cart = apmodels.Cart.objects.get(customer = customer)
                except ObjectDoesNotExist:
                    cart  = apmodels.Cart.objects.create(customer=customer)
                    cart.refresh_from_db()
                try:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product, customer=customer)

                except ObjectDoesNotExist:

                    cartedproduct = apmodels.CartedProduct.objects.create(product=product, customer=customer,quantity = 1)
            
            else:
                try:
                    cart = apmodels.Cart.objects.get(session = request.session.session_key)

                except ObjectDoesNotExist:
                    cart  = apmodels.Cart.objects.create(session=request.session.session_key)
                    cart.refresh_from_db()
                try:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product, session = request.session.session_key)

                except ObjectDoesNotExist:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product, session=request.session.session_key,quantity = 1)

            cartedproduct.quantity = 1
            cartedproduct.save()        
            cart.products.add(cartedproduct)
            output_data = {
            'notification': 'Product added to cart',
            'loadcontent':True,
            'reload_url':redirect('customer_cart_count').url,
            'container':'cart-count'
                            }
            return JsonResponse(output_data)

def add_variation_to_cart(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    customer = False

    if request.method == 'POST':
        productid = str(request.POST.copy().get('productid'))
        variationid = str(request.POST.copy().get('variationid'))
        quantity = int(request.POST.copy().get('quantity'))
        product = apmodels.Product.objects.get(productid=productid)
        try:
            variationid =int(variationid)
        except ValueError:
            variationid = ''

        productvariation = apmodels.ProductVariation.objects.get(id=variationid)

        if request.user.is_authenticated:
            customer = allObject['customer']
            try:
                cart = apmodels.Cart.objects.get(customer = customer)
            except ObjectDoesNotExist:
                cart  = apmodels.Cart.objects.create(customer=customer)
                cart.refresh_from_db()
            try:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,variation__id=variationid, customer=customer)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product, customer=customer)

            except ObjectDoesNotExist:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product,variation=productvariation or None, customer=customer,quantity = quantity)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product, customer=customer,quantity = quantity)
        
        else:
            try:
                cart = apmodels.Cart.objects.get(session = request.session.session_key)

            except ObjectDoesNotExist:
                cart  = apmodels.Cart.objects.create(session=request.session.session_key)
                cart.refresh_from_db()
            try:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,variation__id=variationid, session = request.session.session_key)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product, session = request.session.session_key)

            except ObjectDoesNotExist:
                if variationid:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product,variation=productvariation or None, session=request.session.session_key,quantity = quantity)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.create(product=product, session=request.session.session_key,quantity = quantity)

        cartedproduct.quantity = quantity
        cartedproduct.save()        
        cart.products.add(cartedproduct)
        cart.refresh_from_db()

        output_data = {
        'notification': 'Product added to cart',
        'loadcontent':True,
        'reload_url':redirect('customer_cart_count').url,
        'container':'cart-count'
                        }
        return JsonResponse(output_data) 
    else:
       
        output_data = {
        'notification': 'Invalid request',
                        }
        return JsonResponse(output_data) 


def add_to_saved(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    customer = False
    product = apmodels.Product.objects.get(productid=productid)

    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            saved = apmodels.Saved.objects.get(customer = customer)
        except ObjectDoesNotExist:
            saved  = apmodels.Saved.objects.create(customer=customer)
            saved.refresh_from_db()

    else:
        try:
            saved = apmodels.Saved.objects.get(session = request.session.session_key)

        except ObjectDoesNotExist:
            saved  = apmodels.Saved.objects.create(session=request.session.session_key)
            saved.refresh_from_db()
    if product in saved.products.all():
        output_data = {
        'content': saved.products.all().count(),
        'notification': 'Product already saved',
                        }
    else:
        saved.products.add(product)

        allObject['product'] = product
        add_to_saved_button = 'seller/remove_from_saved_button.html'
        content = loader.render_to_string(add_to_saved_button,allObject,request)
        output_data = {
            'content':content,
        'notification': 'Product saved',
                        }
    return JsonResponse(output_data) 

def remove_from_saved(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    customer = False
    product = apmodels.Product.objects.get(productid=productid)

    if request.user.is_authenticated:
        if request.user.is_superuser:
            try:
                saved = apmodels.Saved.objects.get(session = request.session.session_key)

            except ObjectDoesNotExist:
                saved  = apmodels.Saved.objects.create(session=request.session.session_key)
                saved.refresh_from_db()
        else:
            customer = allObject['customer']
            try:
                saved = apmodels.Saved.objects.get(customer = customer)
            except ObjectDoesNotExist:
                saved  = apmodels.Saved.objects.create(customer=customer)
                saved.refresh_from_db()

    else:
        try:
            saved = apmodels.Saved.objects.get(session = request.session.session_key)

        except ObjectDoesNotExist:
            saved  = apmodels.Saved.objects.create(session=request.session.session_key)
            saved.refresh_from_db()
    if product in saved.products.all():
        saved.products.remove(product)
        allObject['product'] = product
        add_to_saved_button = 'seller/add_to_saved_button.html'
        content = loader.render_to_string(add_to_saved_button,allObject,request)
        output_data = {
            'content':content,
        'notification': 'Product removed from saved',
                        }
    else:
        output_data = {
        'notification': 'Product not saved',
                        }
    return JsonResponse(output_data) 


@seller_login_required
@checksellerstatus
def checkout(request,productid=None, *args, **kwargs):
    allObject = inherit(request)
    customer = False
    if request.method == 'POST':
        if request.user.is_authenticated:
            customer = allObject['customer']
            try:
                cart = apmodels.Cart.objects.get(customer = customer)
            except ObjectDoesNotExist:
                pass
            try:
                order = apmodels.Order.objects.get(customer=customer,complete = False)
            except ObjectDoesNotExist:
                order = apmodels.Order.objects.get(customer=customer)

        else:
            try:
                cart = apmodels.Cart.objects.get(session = request.session.session_key)

            except ObjectDoesNotExist:
                cart  = apmodels.Cart.objects.create(session=request.session.session_key)
                cart.refresh_from_db()
            try:
                cartedproduct = apmodels.CartedProduct.objects.get(product=product, session = request.session.session_key)

            except ObjectDoesNotExist:
                cartedproduct = apmodels.CartedProduct.objects.create(product=product, session=request.session.session_key,quantity = quantity)
    
        cartedproduct.quantity = quantity
        cartedproduct.save()        
        cart.products.add(cartedproduct)

        allObject['message'] = '<span class="text-primary uk-text-bold h1">Product added to cart </span>'
        message_template = 'general/success.html'
        global message
        message = loader.render_to_string(message_template,allObject,request)
        cart.refresh_from_db()
    else:
        template_name = 'seller/checkout.html'
        # customer = allObject['customer']
        allObject['title']='Checkout | '+ allObject['store'].store_name
        if request.user.is_authenticated:
            customer = allObject['customer']
            cart = apmodels.Cart.objects.get(customer = customer)
        else:
            cart = apmodels.Cart.objects.get(session = request.session.session_key)
        # for product in cart.products.all():
        #     product.save()
        cart.save()
        allObject['cart'] = cart or None
        locations = apmodels.DeliveryLocation.objects.all()
        allObject['locations'] = locations

        return render(request,template_name,allObject)




def remove_from_cart(request,id=None, *args, **kwargs):
    allObject = inherit(request)
    customer = False
    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            cart = apmodels.Cart.objects.get(customer = customer)
        except ObjectDoesNotExist:
            pass
        try:
            cartedproduct = apmodels.CartedProduct.objects.get(cartedproductid=id,)
        except ObjectDoesNotExist:
            pass    
    else:
        try:
            cart = apmodels.Cart.objects.get(session = request.session.session_key)

        except ObjectDoesNotExist:
            pass
        try:
            cartedproduct = apmodels.CartedProduct.objects.get(cartedproductid=id,)

        except ObjectDoesNotExist:
            pass
    cartedproduct.delete()        
    cart.save()
    cart.refresh_from_db()

    allObject['cart'] = cart
    content_template = 'seller/cart_container.html'
    content = loader.render_to_string(content_template,allObject,request)

    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 



def index(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/base/base.html'
    store = allObject['store']
    try:
        allObject['title']=store.store_name
    except Exception:
        allObject['title']='Welcome . Intelbyt'
    return render(request,template_name,allObject)


@seller_login_required
def app(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/base/app.html'
    store = allObject['store']
    try:
        allObject['title']=store.store_name
    except Exception:
        allObject['title']='Welcome . Intelbyt'
    content = loader.render_to_string(template_name,allObject,request)
    nexturl = 'seller/dashboard'
    if request.GET.get('next'):
        nexturl =str(request.GET.get('next'))
    try:
        title = 'Welcome - ' + allObject['store'].store_name
    except AttributeError:
        title = ''
    output_data = {
    'content': content,
    'title': title,
    'nexturl':nexturl

                    }
    return JsonResponse(output_data)


@method_decorator(seller_login_required, name='get')
@method_decorator(checksellerstatus, name='get')
class dashboard(View):
    def get(self,request,*args, **kwargs):
        allObject = inherit(request,*args, **kwargs)

        template_name = 'seller/dashboard.html'
        store = allObject['store']
        allObject['title']='DPG | Dashboard'
        allObject['page'] = 'Dashboard'
        allObject['year']=now().year

        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'content': content,
        'page':'Dashboard',
        'title':"Dashboard"
                        }
        return JsonResponse(output_data)
        return render(request,template_name,allObject)

    def getRequest(self):
        return self.request



def downloadorder(request,orderid=None,*args, **kwargs):
    allObject = inherit(request)

    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            order = apmodels.Order.objects.get(customer = customer,orderid=orderid)
        except ObjectDoesNotExist:
            pass
    else:
        try:
            order = apmodels.Order.objects.get(session = request.session.session_key,orderid=orderid)
        except ObjectDoesNotExist:
            pass
    filename= order.orderid
    for product in order.products.all():
        encoded_string = ''
        try:
            with open(product.product.image.path, 'rb') as img_f:
                encoded_string = base64.b64encode(img_f.read()).decode()
            image= 'data:image/%s;base64,%s' % ('png', encoded_string)
            product.product.base64 = image
            product.product.save()    
        except ValueError:
            pass
    order.refresh_from_db()
    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            order = apmodels.Order.objects.get(customer = customer,orderid=orderid)
        except ObjectDoesNotExist:
            pass
    else:
        try:
            order = apmodels.Order.objects.get(session = request.session.session_key,orderid=orderid)
        except ObjectDoesNotExist:
            pass
    allObject['order'] = order

    encoded_string = ''
    
    with open(allObject['store'].logo.path, 'rb') as img_f:
        encoded_string = base64.b64encode(img_f.read()).decode()
    logo= 'data:image/%s;base64,%s' % ('png', encoded_string)
    template_name = 'seller/order_download.html'
    response = PDFTemplateResponse(request=request,
                                    template='seller/order_download.html',
                                    filename=filename+".pdf",
                                    context= {'allObject':allObject,'logo':logo},
                                    show_content_in_browser=False,
                                    cmd_options={
                                        
                                        'page-size': 'A4',
                                        'margin-top': '0in',
                                        'margin-right': '0in',
                                        'margin-bottom': '0in',
                                        'margin-left': '0in',
                                        'encoding': "UTF-8",
                                        'no-outline': None,
                                    "zoom":1,
                                    
                                    'javascript-delay':1000,
                                    'footer-center' :'[page]/[topage]',
                                    "no-stop-slow-scripts":True},
                                    )
    # for product in order.products.all():
    
    #     product.product.base64 = ''
    #     product.product.save()
    return response


def myorder(request,orderid=None, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'seller/my_order.html'
    # customer = allObject['customer']
    allObject['title']='My Order | '+ allObject['store'].store_name
    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            order = apmodels.Order.objects.get(customer = customer,orderid=orderid)
        except ObjectDoesNotExist:
            pass
    else:
        try:
            order = apmodels.Order.objects.get(session = request.session.session_key,orderid=orderid)
        except ObjectDoesNotExist:
            pass
    allObject['order'] = order or None

    return render(request,template_name,allObject)


def orderpaid(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']
    if request.method == 'POST':
        orderid = request.POST.copy().get('orderid')
        order = apmodels.Order.objects.get(orderid=orderid)
        order.payment_method = 'op'
        order.paid=True
        order.date_time_paid =datetime.datetime.now()
        order.save()
        for product in order.products.all():
            product.product.purchase_count +=1
            product.product.save()
        # orders = apmodels.Order.objects.filter(customer=customer,)

        subject = 'New Order Placed - '+order.orderid

        message = render_to_string('seller/order_placed_email.html', {
                'order':order,
                'customer':customer,
            'title':'ORDER PLACED',
            'socials':gmodels.SocialLink.objects.all(),
            'store':allObject['store']
            })
        recipient_list = [allObject['store'].email, ]
        to = recipient_list
        subject = subject
        body = message
        sendmail(to,body,body,subject)
        subject = 'New Order Placed - '+order.orderid

        message = render_to_string('seller/customer_order_placed_email.html', {
                'order':order,
                'customer':customer,
                'title':'ORDER PLACED',
                'socials':gmodels.SocialLink.objects.all(),
                'store':allObject['store']
            })
        recipient_list = [customer.email, ]
        to = recipient_list
        subject = subject
        body = message
        sendmail(to,body,body,subject)
        if order.delivery_option == 'd':
            message = "<span class='text-primary uk-text-bold h1'>Order placed successful.</span>"
        elif order.delivery_option == 'p':
            message = "<span class='text-primary uk-text-bold h1'>Order placed successful.</span> <br> <p class='text-darker'> Your order is ready for pickup </p>"
        
        template_name = 'general/success.html'
        allObject['message'] = message
        message = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'modal_message': message,
        'status':'success',
        'url':redirect('customer_home').url
                        }
        return JsonResponse(output_data)  
    else:
        output_data = {
        'success': False,
                        }
        return JsonResponse(output_data)    


def payondelivery(request,orderid=None, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']
    order = apmodels.Order.objects.get(orderid=orderid)
    order.payment_method = 'pd'
    # order.paid=True
    # order.date_time_paid =datetime.datetime.now()
    order.save()
    # orders = apmodels.Order.objects.filter(customer=customer,)
    order.refresh_from_db()
    for product in order.products.all():
        product.product.purchase_count +=1
        product.product.save()
    subject = 'New Order Placed - '+order.orderid

    message = render_to_string('seller/order_placed_email.html', {
            'order':order,
            'customer':customer,
            'title':'ORDER PLACED',
            'socials':gmodels.SocialLink.objects.all(),
            'store':allObject['store']
        })
    recipient_list = [allObject['store'].email, ]
    to = recipient_list
    subject = subject
    body = message
    sendmail(to,body,body,subject)
    subject = 'New Order Placed - '+order.orderid

    message = render_to_string('seller/customer_order_placed_email.html', {
            'order':order,
            'customer':customer,
            'title':'ORDER PLACED',
            'socials':gmodels.SocialLink.objects.all(),
            'store':allObject['store']
        })
    recipient_list = [customer.email, ]
    to = recipient_list
    subject = subject
    body = message
    sendmail(to,body,body,subject)
    if order.delivery_option == 'd':
        message = "<span class='text-primary uk-text-bold h1'>Order placed successful.</span>"
    elif order.delivery_option == 'p':
        message = "<span class='text-primary uk-text-bold h1'>Order placed successful.</span> <br> <p class='text-darker'> Your order is ready for pickup </p>"
    
    template_name = 'general/success.html'
    allObject['message'] = message
    message = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'modal_message': message,
    'status':'success',
    'url':redirect('customer_home').url
                    }
    return JsonResponse(output_data)  
   


@seller_login_required
@checksellerstatus
def investmentsuccessful(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']

    if request.method == 'POST':
        investmentid = request.POST.copy().get('investmentid')
        investment = apmodels.Investment.objects.get(investmentid=investmentid)
        investment.successful=True
        investment.date_time_approved = datetime.datetime.now()
        # investment.due_date_time = datetime.datetime.fromtimestamp((datetime.datetime.timestamp(datetime.datetime.now()) + (259200*investment.months)))
        investment.due_date_time = datetime.datetime.now()+relativedelta(months=investment.months)
        investment.save()
        template_name = 'general/success.html'
        message = "<span class='text-primary uk-text-bold h1'>Investment was successfully added.</span>"
        allObject['message'] = message
        message = loader.render_to_string(template_name,allObject,request)
        output_data = {
        'modal_message': message,
        'success':True
                        }
        return JsonResponse(output_data)  
    else:
        output_data = {
        'success': False,
                        }
        return JsonResponse(output_data)    




@seller_login_required
@checksellerstatus
def investmentbrief(request, *args, **kwargs):
    allObject = inherit(request)
    amount = int(request.POST.copy().get('amount'))
    months = int(request.POST.copy().get('months'))
    interest_rates = [2,4.5,7.5,11,15,19.5,24.5,30,36,42.5,49.5,57]
    interest_rate = interest_rates[months-1]
    interest =  interest_rate/100 * amount
    total = amount +interest
    formatted_amount = '{:,.2f}'.format(amount)
    formatted_interest = '{:,.2f}'.format(interest)
    formatted_total = '{:,.2f}'.format(total) 
    allObject['amount']=formatted_amount
    allObject['total'] = formatted_total
    allObject['interest'] = formatted_interest
    allObject['months'] = months
    allObject['interestrate'] = interest_rate
    template_name = 'seller/investment_brief.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'details':content,
                    }
    return JsonResponse(output_data)



@seller_login_required
@checksellerstatus
def checkfetchaccountnumber(request, *args, **kwargs):
    allObject = inherit(request)
    account_number = request.POST.copy().get('account_number')
    try:
        account = apmodels.SavingsAccount.objects.get(number=account_number)
        output_data = {
        'full_name':account.customer.full_name,
                        }
        return JsonResponse(output_data)
    except ObjectDoesNotExist:
        output_data = {
        'full_name':'Account number does not exist',
                        }
        return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def checkaccountnumber(request, *args, **kwargs):
    allObject = inherit(request)
    account_number = request.POST.copy().get('account_number')
    account_bank = request.POST.copy().get('account_bank')
    verification_response = Verification.verify_account(account_number=account_number,bank_code=account_bank)
    if verification_response['status']:
        output_data = {
        'full_name':verification_response['data']['account_name'],
                        }
        return JsonResponse(output_data)
    else:
        output_data = {
        'full_name':'Wrong account details',
                        }
        return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def directqrccredit(request,pin, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']
    qr = False
    cpin = False
    if customer.profile_updated:
        if request.method == 'POST':
            try:
                savingsaccount = apmodels.SavingsAccount.objects.get(number=str(request.POST.copy().get('qrcoderesult')))
                credit_customer = savingsaccount.customer
            except ObjectDoesNotExist:
                output_data = {
                    'done':True,
                    'modal_message':'Account not found',
                                }        
                                
                return JsonResponse(output_data)
            if credit_customer == customer:
                output_data = {
                'done':True,
                'modal_message':'Cannot share to same account!',
                            }        
                            
                return JsonResponse(output_data)
            pin = str(pin)
            pin_digits= pin.split('-')
            counter = 0
            # temporary_digits = ''
            # for digit in pin:
            #     temporary_digits += digit
            #     if len(temporary_digits) == 4:
            #         pin_digits.append(temporary_digits)
            #         temporary_digits =''
            pin_4_digits = pin_digits[3]
            pin_12_digits = pin_digits[0]+pin_digits[1]+pin_digits[2]
            try:
                pin = apmodels.CreditPin.objects.get(pin=pin_12_digits,last_4_digits=pin_4_digits)
                if pin.used:
                    if pin in credit_customer.used_pins.all():
                        if qr:
                            message ='<span class="text-danger uk-text-bold h4">QRCode already used by this customer!</span> <br> You will be suspended if you retry this QRCode code upto 5 times'
                        elif cpin:
                            message ='<span class="text-danger uk-text-bold h4">Pin already used by this customer!</span> <br> You will be suspended if you retry this PIN upto 5 times'
                    else:
                        if qr:
                            message ='<span class="text-danger uk-text-bold h4">QRCode already used by another customer!</span> <br> You will be suspended if you retry this QRCode code upto 5 times'
                        elif cpin:
                            message ='<span class="text-danger uk-text-bold h4">Pin already used by another customer!</span> <br> You will be suspended if you retry this PIN upto 5 times'                
                else:
                    creditaccount(request,credit_customer,pin.amount)

                    pin.used=True
                    pin.used_by = credit_customer.customerid
                    pin.save()
                    debit_customer =apmodels.Customer.objects.get(customerid=pin.generated_by)
                    debitaccount(request,debit_customer, pin.amount)
                    credit_customer.used_pins.add(pin)
                    share = apmodels.ShareTransaction.objects.create(from_customer = debit_customer,to_customer=credit_customer,pin=pin)
                    interest = apmodels.Interest.objects.create(customer=debit_customer,amount=pin.amount*0.05,associateid=share.transactionid)
                    debit_customer.savings_account.balance+=interest.amount
                    debit_customer.savings_account.save()
                    debit_customer.save()
                    updatesavingsrating(credit_customer,allObject)
                    template_name = 'general/success.html'
                    message = "Receiver's account has been credited with <span class='text-primary uk-text-bold h1'>N" +pin.formatted_amount + "</span>"
                    allObject['message'] = message
                    message = loader.render_to_string(template_name,allObject,request)
            except ObjectDoesNotExist:
                        message ='<span class="text-danger uk-text-bold h4">Invalid Credit credentials</span> <br> You will be suspended if you retry this QRCode code upto 5 times'
                        
            output_data = {
                'done':True,
                'modal_message':message,
                            }        
                            
            return JsonResponse(output_data)
    else:
        output_data = {
        'modal_message':'Kindly update your profile',
                        }
        return JsonResponse(output_data)



def sufficientbalance(function):
    def checksufficientbalance(*args,**kwargs):
        allObject = inherit(*args, **kwargs)
        customer = allObject['customer']
        if args[0].method =='POST':
            if customer.savings_account.balance < int(args[0].POST.copy().get('amount')):
                output_data = {
                        'modal_message':'Insufficient balance',  
                                }
                return JsonResponse(output_data)
        
        return function(*args,**kwargs)
    return checksufficientbalance



@seller_login_required
@checksellerstatus
@sufficientbalance
def generatepinqrcode(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']
    if request.method == 'POST':
        amount = int(request.POST.copy().get('amount'))
        try:
            pin =  apmodels.CreditPin.objects.filter(amount=amount,used=False,generated_by=customer.customerid)[0]
        except:
            pin = apmodels.CreditPin.objects.create(amount=amount,generated_by=customer.customerid)
        pin.refresh_from_db()
        qrtext= pin.pin+pin.last_4_digits
        # +3600000.0 
        allObject['qrtext'] = qrtext
        allObject['pin'] = pin

        template_name = 'seller/qrcode_response.html'
        allObject['qrc_options'] =QRCodeOptions(qrtext,custom_text=qrtext, size='18', border=8, error_correction='L',image_format='png')
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'full_modal':content,  
                        }
        return JsonResponse(output_data) 

@seller_login_required
@checksellerstatus
def creditmodalcontent(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']
    account_number = customer.savings_account.number
    allObject['qrc_options'] =QRCodeOptions(account_number,custom_text=account_number, size='10', border=8, error_correction='L',image_format='png')

    template_name = 'seller/credit_modal_content.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
                        'content':content,
                    }
    return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def share(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']

    template_name = 'seller/share_form.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
                        'content':content,
                        'title':'Fetch Share'
                    }
    return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
@sufficientbalance
def withdraw(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']

    if request.method =='POST':
        amount = int(request.POST.copy().get('amount'))
        customer_account = apmodels.CustomerAccount.objects.get(customer=customer,deleted=False)
        withdrawal = apmodels.WithdrawalTransaction.objects.create(customer=customer, amount=int(amount),customer_account=customer_account,)
        withdrawal.refresh_from_db()
        debitaccount(request,customer,withdrawal.amount)
        message_template_name = 'general/success.html'
        message = '<span class="text-primary uk-text-bold h2">Withdrawal successfull </span>'
        allObject['message'] = message
        message = loader.render_to_string(message_template_name,allObject,request)
        output_data = {
                            'modal_message':message,
                        }
        return JsonResponse(output_data) 
    else:
        try:
            customer_account = apmodels.CustomerAccount.objects.get(customer=customer)
            template_name = 'seller/withdrawal_form.html'
        except ObjectDoesNotExist:
            bank = apmodels.Bank.objects.get(name='Gtbank')
            allObject['bank']=bank
            template_name = 'seller/no_account.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Fetch Withdrawal'
                        }
        return JsonResponse(output_data)




@seller_login_required
@checksellerstatus
def verifydeposit(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']

    if request.method =='POST':
        reference =str(request.POST.copy().get('reference'))

        deposit = apmodels.DepositTransaction.objects.get(customer=customer, transactionid=reference,)
        deposit.refresh_from_db()
        depositsuccessful = verifypaymentinine(request,reference)
        if depositsuccessful:
            creditaccount(request,customer,deposit.amount)
            deposit.successful = True
            deposit.save()
        message_template_name = 'general/success.html'
        message = 'Deposit of <span class="text-primary uk-text-bold h2">₦'+deposit.formatted_amount+' was successfull'
        allObject['message'] = message            
        message = loader.render_to_string(message_template_name,allObject,request)
        output_data = {
                            'modal_message':message,
                        }
        return JsonResponse(output_data) 




@seller_login_required
@checksellerstatus
def verifyinvestment(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']

    if request.method =='POST':
        reference =str(request.POST.copy().get('reference'))

        investment = apmodels.Investment.objects.get(customer=customer, investmentid=reference,)
        investment.refresh_from_db()
        investmentsuccessful = verifypaymentinine(request,investment.investmentid)
        if investmentsuccessful:
            investment.successful = True
            investment.save()
        message_template_name = 'general/success.html'
        message = 'Investment of <span class="text-primary uk-text-bold h2">₦'+investment.formatted_amount+' was successfull'
        allObject['message'] = message            
        message = loader.render_to_string(message_template_name,allObject,request)
        output_data = {
                            'modal_message':message,
                            'success':True
                        }
        return JsonResponse(output_data) 



@seller_login_required
@checksellerstatus
def deposit(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']

    if request.method =='POST':
        amount =float( str(request.POST.copy().get('amount')).replace(',',''))
        deposit = apmodels.DepositTransaction.objects.create(customer=customer, amount=amount,)
        deposit.refresh_from_db()
        output_data = {
                            'depositid':deposit.transactionid,
                            'depositamount':deposit.amount,
                            'customeremail':customer.email,
                            'created':True
                        }
        return JsonResponse(output_data) 
    else:

        template_name = 'seller/deposit_form.html'
        
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Fetch Deposit'
                        }
        return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def invest(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']

    if request.method =='POST':
        amount =float( str(request.POST.copy().get('amount')).replace(',',''))
        months =int(request.POST.copy().get('months'))
        investment = apmodels.Investment.objects.create(customer=customer, amount=amount,months=months)
        investment.refresh_from_db()
        output_data = {
                            'investmentid':investment.investmentid,
                            'investmentamount':investment.amount,
                            'customeremail':customer.email,
                            'created':True
                        }
        return JsonResponse(output_data) 
    else:

        template_name = 'seller/invest_form.html'
        
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Fetch Invest'
                        }
        return JsonResponse(output_data)


@seller_login_required
@checksellerstatus
def addaccount(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']
    if request.method =='POST':
        bank_code = request.POST.copy().get('bank')
        account_number = request.POST.copy().get('account_number')
        bank = apmodels.Bank.objects.get(code=bank_code)
        account_number = apmodels.CustomerAccount.objects.create(customer=customer, bank=bank,number=account_number)
        account_number.refresh_from_db()
        message_template_name = 'general/success.html'
        message = 'Account details added successfully'
        allObject['message'] = message            
        message = loader.render_to_string(message_template_name,allObject,request)
        output_data = {
                            'modal_message':message,
                        }
        return JsonResponse(output_data) 
    else:
        banks = apmodels.Bank.objects.all()
        allObject['banks']= banks
        template_name = 'seller/add_account_form.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Add Account Number'
                        }
        return JsonResponse(output_data)



@seller_login_required
@checksellerstatus
def choosetransferdestination(request,destination=None, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']
    template_name = 'seller/choose_transfer_destination.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
                        'content':content,
                        'title':'Choose destination'
                    }
    return JsonResponse(output_data)




@seller_login_required
@checksellerstatus
@sufficientbalance
def internaltransfer(request, *args, **kwargs):
    allObject = inherit(request)
    customer = allObject['customer']
    if request.method =='POST':
        fetch_account_number = request.POST.copy().get('account_number')
        amount =int(request.POST.copy().get('amount'))
        account_number = request.POST.copy().get('account_number')
        try:
            fetch_account = apmodels.SavingsAccount.objects.get(number=fetch_account_number)
        except ObjectDoesNotExist:
            output_data = {
                                'modal_message':'Account does not exist',
                            }
            return JsonResponse(output_data)
        if customer.business_mode and not fetch_account.customer.business_mode:
            output_data = {
                                'modal_message':'Cannot transfer to this account because it is a non-business account',
                            }
            return JsonResponse(output_data)
        if customer == fetch_account.customer:
            output_data = {
                                'modal_message':'Cannot transfer to same account',
                            }
            return JsonResponse(output_data)
        transfer = apmodels.FetchTransfer.objects.create(customer=customer, amount=amount,fetch_account=fetch_account,account_number=account_number)
        transfer.refresh_from_db()
        debitaccount(request,customer,transfer.amount)
        creditaccount(request,fetch_account.customer,transfer.amount)

        message_template_name = 'general/success.html'
        message = '<span class="text-primary uk-text-bold h2">Transfer successfull </span> <br> <br> <button class="btn btn-primary rounded-pill">View receipt</button>'
        allObject['message'] = message            
        message = loader.render_to_string(message_template_name,allObject,request)

        output_data = {
                            'modal_message':message,
                        }
        return JsonResponse(output_data) 
    else:
        banks = apmodels.Bank.objects.all()
        allObject['banks']= banks
        template_name = 'seller/internal_transfer_form.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Transfer to Fetch account'
                        }
        return JsonResponse(output_data)



def sellerlookup(request,inline=False, *args, **kwargs):
    allObject = inherit(request)
    if request.user.is_authenticated:
        auth.logout(request)
    # if request.user.is_authenticated:
    #     logout(request)
    #     return redirect('account_login')
    url = str(request.GET.get('next'))
    print('next urls = ' + url)
    store = admodels.Store.objects.all()[0]
    allObject['store'] = store
    try:
        allObject['title']=allObject['settings'].store_name +' | Login In'
    except Exception:
        allObject['title']='Intelbyt | Login In'
    seller = False
    if request.method == 'POST':

        uniqueidentifier = request.POST.copy().get('identifier').lower()
        try:
            user = User.objects.get(email=uniqueidentifier)
            seller = smodels.Seller.objects.get(user=user)

        except ObjectDoesNotExist:
            try:
                user = User.objects.get(username=uniqueidentifier)
                seller = smodels.Seller.objects.get(user=user)
            except ObjectDoesNotExist:

                output_data = {
                    'invalid':True,
                    'error':'Record not found.'
                }
                return JsonResponse(output_data)

        if request.POST.copy().get('next'):
            allObject['next_page']=request.POST.copy().get('next')
            allObject['redirect_url']=''.join(tuple(request.POST.copy().get('next')))
        allObject['identifier']=uniqueidentifier

        template_name = 'allauth/account/seller_enter_password.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                    'form_content':content,
                }
        return JsonResponse(output_data)

    else:
        form = allauthforms.LoginForm()
        allObject['form'] = form
        if request.GET.get('next'):
            allObject['next_page']=request.GET.get('next')
            allObject['redirect_url']=''.join(tuple(request.GET.get('next')))
        template_name = 'allauth/account/seller_lookup.html'
        nexturl = redirect('seller_dashboard').url

        if request.GET.get('next'):
            nexturl =str(request.GET.get('next'))
        # return render(request,template_name,allObject)
        allObject['nexturl'] = nexturl
        content = loader.render_to_string(template_name,allObject,request)

        # if inline:

        #     return True



        output_data = {
                            'content':content,
                            'title':'Login',
                            'login':True,
                            'nexturl':nexturl.split('?')[0]

                        }
        return JsonResponse(output_data)



def logoutuser(request, *args, **kwargs):
    auth.logout(request)
    form = allauthforms.LoginForm()
    allObject['form'] = form
    if request.GET.get('next'):
        allObject['next_page']=request.GET.get('next')
        allObject['redirect_url']=''.join(tuple(request.GET.get('next')))
    template_name = 'allauth/account/seller_lookup.html'
    # return render(request,template_name,allObject)
    content = loader.render_to_string(template_name,allObject,request)

    output_data = {
                        'content':content,
                        'title':'Login',
                        'login':True,
                        'nexturl':request.GET.get('next') or redirect('seller_dashboard').url
                    }
    return JsonResponse(output_data)


def sellersignup(request, *args, **kwargs):
    allObject = inherit(request)
    store = admodels.Store.objects.all()[0]
    allObject['store'] = store
    if request.method == 'POST':
        chars = '0123456789' 
        token = ''
        for num in range(0,len(chars)):
            token = token +chars[round((random()-0.5)*len(chars))]
        token = token[0:6]
        user_id = 'D'+str(round(random()*123456789090929))
        user_id = user_id[0:10]
        # form.user_id = user_id
        chars = '0123456789' 
        token = ''
        for num in range(0,len(chars)):
            token = token +chars[round((random()-0.5)*len(chars))]
        token = token[0:6]                        
        erroroutput ="<ul class='text-danger p-0'>"
        errorlist = ''
        formerrors = []
        email =str(request.POST.copy().get('email')).lower()
        username = str(request.POST.copy().get('username')).lower()
        password = str(request.POST.copy().get('password'))
        first_name =str(request.POST.copy().get('first_name'))
        last_name= str(request.POST.copy().get('last_name'))
        harshed_password = make_password(password)
        if email:
            try:
                user = User.objects.get(email=email)
                formerrors.append('<li>Email already taken</li>')
            except ObjectDoesNotExist:
                try:
                    profile = apmodels.Customer.objects.get(email=email)
                    formerrors.append('<li>Email already taken</li>')
                except ObjectDoesNotExist:
                    pass  
        if username:
            try:
                user = User.objects.get(username=username)
                formerrors.append('<li>Username already taken</li>')
            except ObjectDoesNotExist:
                pass  
        if len(formerrors) >0:
            erroroutput ="<ul class='text-danger p-0 ml-4'>"
            errorlist = ''
            for error in formerrors:
                errorlist += str(error)
            erroroutput += errorlist + '</ul>'
            output_data = { 
                            'invalid':True,
                            'modal_notification':'<b>Ooops... Something is wrong!</b>' + erroroutput,
                            
                        }
            return JsonResponse(output_data)
        user = User.objects.create(password=harshed_password, username=username,
        first_name =first_name,last_name= last_name, email= email)
        user.refresh_from_db()
        user.is_active = True
        user.save()
        seller = smodels.Seller.objects.create(user=user)
        login(request, user)
        allObject = inherit(request)
        if request.POST.copy().get('next'):
            redirectinstance= redirect(request.POST.copy().get('next'))
            redirecturl = redirectinstance.url
        else:
            redirecturl = redirect('seller_dashboard').url
        output_data = {
                            'logged_in':True,
                            'redirecturl':redirecturl
                        }
        return JsonResponse(output_data)
  
    else:
        form = allauthforms.LoginForm()
        allObject['form'] = form
        print('cool')
        if request.GET.get('next'):
            allObject['next_page']=request.GET.get('next')
            allObject['redirect_url']=''.join(tuple(request.GET.get('next')))
        template_name = 'allauth/account/seller_signup.html'
        nexturl = redirect('seller_dashboard').url

        if request.GET.get('next'):
            nexturl =str(request.GET.get('next'))
        # return render(request,template_name,allObject)
        allObject['nexturl'] = nexturl
        content = loader.render_to_string(template_name,allObject,request)

        # if inline:

        #     return True



        output_data = {
                            'content':content,
                            'title':'Login',
                            'signup':True,
                            'nexturl':nexturl.split('?')[0]

                        }
        return JsonResponse(output_data)

def loginuser(request, *args, **kwargs):
    if request.method == 'POST':
        username = request.POST.copy().get('username').lower()
        raw_password = request.POST.copy().get('password')
        try:
            userObject = User.objects.get(username=username,is_active=True)
        except ObjectDoesNotExist:
            try:
                userObject = User.objects.get(email=username,is_active=True)
            except ObjectDoesNotExist:
                output_data = {
                    'invalid':True,
                    'modal_notification':'Invalid login details'
                }
                return JsonResponse(output_data)
        user = authenticate(username=userObject.username, password=raw_password)


        if user:
            login(request, user)
        else:
            output_data = {
            'invalid':True,
            'modal_notification':'Invalid password'
                }
            return JsonResponse(output_data)
        output_data = {
        # 'content': content,
        'logged_in':True,
                        }
        return JsonResponse(output_data) 




    else:
        form = allauthforms.LoginForm()
        allObject['form'] = form
        if request.GET.get('next'):
            allObject['next_page']=request.GET.get('next')
            allObject['redirect_url']=''.join(tuple(request.GET.get('next')))
        template_name = 'allauth/account/login.html'
        return render(request,template_name,allObject)
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                        }
        return JsonResponse(output_data)

