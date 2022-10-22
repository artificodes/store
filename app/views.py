from logging import exception
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from allauth.account.views import SignupView
import app

from django.core.exceptions import ObjectDoesNotExist

from random import random
from django.contrib.auth.hashers import check_password, make_password
from django.contrib import auth
from django.contrib.auth.models import User
from django.utils.encoding import force_text
from django.utils.http import urlsafe_base64_decode
from django.contrib.sites.models import Site
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from app.email_sender import sendmail
from general.tokens import account_activation_token
import smtplib
import socket
from django.shortcuts import get_object_or_404
from django.views.generic.edit import FormView
from django.contrib import messages
from django.http import HttpResponse
from django.views import View
from django.views.generic.base import TemplateView
from django.http import HttpResponseRedirect
import os
import base64
from django.forms import ModelForm
from django.conf import settings
from django import forms
import datetime
from allauth.account.views import AjaxCapableProcessFormViewMixin
from django.contrib.auth.decorators import login_required
from random import random
from django.core.paginator import Paginator,PageNotAnInteger,EmptyPage
from django.template import loader
from django.http import JsonResponse
from django.urls import reverse_lazy
from allauth.account import forms as allauthforms
from django.core.mail import send_mail
from app import models as apmodels
from ipware import get_client_ip
import geoip2.database
import requests
import json
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from paystackapi.verification import Verification
from seller import models as smodels
from store_admin import models as admodels
paystack_secret_key = "sk_test_e6c40e9e83237dbb32096831467c6e6193a970cb"
paystack = Paystack(secret_key=paystack_secret_key)


allObject = {}
message = ''

def logrequest(request,customerid=''):
    hostname = socket.gethostname()
    ip_1 = socket.gethostbyname(hostname)
    ip_2, is_routable = get_client_ip(request)
    if ip_2 is None:
        pass
    else:
        # We got the client's IP address
        if is_routable:
            pass
            # The client's IP address is publicly routable on the Internet
        else:
            pass
            # The client's IP address is private
    # try:
    #     response = requests.get('https://api.ipify.org').text
    # # result  = response.json()
    #     location = response
    # except Exception:
    #     location=''
    requestlog = apmodels.VisitorsLog.objects.create(customerid=customerid, url = request.path,ip_1=ip_1,ip_2=ip_2,host_name=hostname,)
    return True


def customer_login_required(function):
    
    def checkstatus(request,*args,**kwargs):
        url = str(request.get_full_path())
        if request.user.is_anonymous:
            return redirect(redirect('customer_login').url +'?next='+url) 
        else:
            return function(request,*args,**kwargs)

    return checkstatus

def inherit(request,id=None):
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
    categories = list(apmodels.Category.objects.all())
    topcategories = filter(lambda x:x.is_top == True,categories)
    allObject['categories'] = categories
    allObject['topcategories'] = topcategories
    allObject['server_timestamp'] = round(datetime.datetime.now().timestamp())
    if request.user.is_anonymous:
        customer = ''        
        allObject['customer'] = ''
        try:
            orders = apmodels.Order.objects.filter(session = request.session.session_key,).values()
            allObject['orders'] = orders

        except ObjectDoesNotExist:
            pass
        try:
            saved = apmodels.SavedProduct.objects.get(session = request.session.session_key,).value()
            allObject['saved'] = len(saved.products.all()) or 0

        except ObjectDoesNotExist:
            pass    
    else:
        user = User.objects.get(pk=request.user.pk)
        try:
            current_user = apmodels.Customer.objects.get(user=user).values()
            allObject['user'] = user
            allObject['customer'] = current_user
            customer = allObject['customer']      
            orders = apmodels.Order.objects.filter(customer = customer,deleted=False).values()
            allObject['orders'] = orders
            try:
                saved = apmodels.SavedProduct.objects.get(customer = customer,).values()
                allObject['saved'] = len(saved.products.all()) or 0
            except ObjectDoesNotExist:
                pass            
        except ObjectDoesNotExist:
            print('here')
            pass
    allObject['store'] = ''
    try:
        store = admodels.Store.objects.all().values()
        allObject['store'] = store
    except ObjectDoesNotExist:
        pass
    socialplatforms = admodels.SocialLink.objects.all().values()
    allObject['socialmediaplatforms'] = socialplatforms
    productgroups = apmodels.Category.objects.all().values()
    allObject['groupproducts'] = productgroups

    return allObject


def verifypayment(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    reference = request.POST.copy().get('reference')
    notconnected = True
    while notconnected:
        try:
            verification_response = Transaction.verify(reference=reference)
            notconnected = False
        except exception:
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

@customer_login_required
def verifypaymentinine(request, reference):
    reference =reference
    notconnected = True
    while notconnected:
        try:
            verification_response = Transaction.verify(reference=reference)
            notconnected = False
        except exception:
            pass
    if verification_response['status'] == True:

        return True
    else:

        return False


@customer_login_required
def confirmemail(request,updated=False, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/email_confirmation_form.html'
    return render(request,template_name,allObject)
    return JsonResponse(output_data)  




@customer_login_required
def confirmemailpage(request,updated=False, *args, **kwargs):
    

    logrequest(request,'')

    allObject = inherit(request, *args, **kwargs)
    url = str(request.get_full_path())
    customer = allObject['customer']

    if customer.privacy_terms_accepted:
        pass
    else:
        return redirect(redirect('accept_privacy_terms').url +'?next='+url) 
    template_name = 'app/templates/email_confirmation_page.html'
    allObject['title'] = 'DPG | Confirm email'
    allObject['page'] = 'Account activation'
    allObject['next'] = request.GET.get('next')
    return render(request,template_name,allObject)
    return JsonResponse(output_data)  




def checkcustomerstatus(request, customer):
    url = str(request.get_full_path())
    if customer.privacy_terms_accepted:
        pass
    else:
        return redirect(redirect('accept_privacy_terms').url +'?next='+url) 

    if customer.email_confirmed:
        pass
    elif not customer.email_confirmed and (customer.email =='' or customer.email =='none'):
        pass
    elif not customer.email_confirmed:
        return redirect(redirect('customer_confirm_email_page').url +'?next='+url)
    else:
        pass
    # if customer.account_type_selected:
    if customer.profile_updated:
        pass
    else:
        return redirect(redirect('customer_update_profile').url +'?next='+url) 
    # else:
    #     return  redirect(redirect('customer_select_account_type').url +'?next='+url)

    return True




@customer_login_required
def select_account_type(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    customer =allObject['customer'] 
    allObject['title'] = 'DPG | Account selection'
    allObject['page'] = 'Account selection'
    allObject['next'] = request.GET.get('next') or '/'
    customerstatus = checkcustomerstatus(request, customer)
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

    template_name = 'app/templates/select_account_type.html'
    return render(request,template_name,allObject)




def cartpage(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/cart.html'
    # customer = allObject['customer']
    allObject['title']='Cart | Intelbyt'
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


def cart(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template = 'app/templates/cart_container.html'
    # customer = allObject['customer']
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
    content= render_to_string(template,allObject,request)
    output_data = {
    'content': content,
        'loadcontent':True,
    'containers':['cart-count']
                    }
    return JsonResponse(output_data) 

@customer_login_required
def updatecontactdetails(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/cart.html'
    allObject['title']='Update contact details | Intelbyt'
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
    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/search_result.html'
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
    allObject = inherit(request, *args, **kwargs)
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
    for product in order.products.all():
        product.delete()
    order.deleted = True
    order.save() 
    subject = 'Order Cancelled - '+id

    message = render_to_string('app/templates/order_cancelled.html', {
            'order':order,
            'title':'ORDER CANCELED',
            'socials':admodels.SocialLink.objects.all(),
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
    content_template = 'app/templates/order_container.html'
    content = loader.render_to_string(content_template,allObject,request)

    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

def myorders(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/my_orders.html'
    # customer = allObject['customer']
    allObject['title']='My orders | Intelbyt'
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
    allObject = inherit(request, *args, **kwargs)
    

    logrequest(request,'')

    template_name = 'app/templates/all_products.html'
    # customer = allObject['customer']
    allObject['title']='All products | Intelbyt'
    all_products = apmodels.Product.objects.all()
    return render(request,template_name,allObject)


def home(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    logrequest(request,'')

    template_name = 'app/templates/home.html'
    # customer = allObject['customer']
    allObject['title']='Home | Intelbyt'
    allObject['page'] = 'Dashboard'
    brands = apmodels.Brand.objects.all()
    allObject['brands'] = brands


    try:
        flashsale = apmodels.FlashSale.objects.filter(end_date_time__gte=datetime.datetime.now(),start_date_time__lte =datetime.datetime.now())[0]
        allObject['flashsale'] = flashsale    
    except Exception:
        pass

    special_packages = apmodels.Product.objects.filter(special_package=True)
    allObject['specialpackages'] = special_packages
    slideshows = apmodels.SlideShow.objects.all()
    allObject['slideshows'] = slideshows
    return render(request,template_name,allObject)


def storehome(request,slug, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    

    logrequest(request,'')
    store = smodels.Store.objects.get(slug=slug,is_approved=True)
    allObject['currentstore'] = store
    template_name = 'app/templates/store_home.html'
    # customer = allObject['customer']
    allObject['title']=store.store_name
    return render(request,template_name,allObject)


def storeproducts(request,slug=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    store = smodels.Store.objects.get(slug=slug)
    # for product in store.products.all():
    #     product.save()
    allproducts = store.products.all()[:10]

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
    allObject['section'] =store.slug

    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def categorys(request,name=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/category_page.html'
    # customer = allObject['customer']
    category = apmodels.Category.objects.get(name=name)

    allObject['title']=category.name +' | Intelbyt'
    allObject['category']=category

    return render(request,template_name,allObject)



def slideshowpage(request,slug=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    

    logrequest(request,'')

    template_name = 'app/templates/slideshow_page.html'
    # customer = allObject['customer']
    slideshow = apmodels.SlideShow.objects.get(slug=slug)

    allObject['title']=slideshow.name+ ' '+ allObject['store'].store_name
    allObject['slideshow']=slideshow

    return render(request,template_name,allObject)


def slideshowproducts(request,slug=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    slideshow = apmodels.SlideShow.objects.get(slug=slug)
    products = list(slideshow.products.all())
    products.sort(key=lambda x:x.date_time_added,reverse=True)
    # for product in products:
    #     product.save()
    allObject['products'] = products
    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 



def brandpage(request,slug=None, *args, **kwargs):
    

    logrequest(request,'')

    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/brand_page.html'
    # customer = allObject['customer']
    brand = apmodels.Brand.objects.get(slug=slug)

    allObject['title']=brand.name+ ' '+ allObject['store'].store_name
    allObject['brand']=brand

    return render(request,template_name,allObject)


def brandproducts(request,slug=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    brand = apmodels.Brand.objects.get(slug=slug)
    products = list(brand.products.all())
    products.sort(key=lambda x:x.date_time_added,reverse=True)
    # for product in products:
    #     product.save()
    allObject['products'] = products
    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def flashsalespage(request,*args, **kwargs):
    

    logrequest(request,'')

    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/flash_sales_page.html'
    # customer = allObject['customer']
    flashsale = apmodels.FlashSale.objects.all()[0]

    allObject['title']='Flashsale | Intelbyt'
    allObject['flashsale']=flashsale

    return render(request,template_name,allObject)


def homegroup(request,slug=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/home_group_page.html'
    # customer = allObject['customer']
    home_group = apmodels.HomePageGroup.objects.get(slug=slug)

    allObject['title']=home_group.name+' '+ allObject['store'].store_name
    allObject['homegroup']=home_group
    allObject['section'] =home_group.slug

    return render(request,template_name,allObject)


def saveditemspage(request,slug=None, *args, **kwargs):
    

    logrequest(request,'')

    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/saved_items_page.html'
    # customer = allObject['customer']

    allObject['title']='Saved Items | Intelbyt'

    return render(request,template_name,allObject)


def savedproducts(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            saved = apmodels.SavedProduct.objects.get(customer = customer)
        except ObjectDoesNotExist:
            saved  = apmodels.SavedProduct.objects.create(customer=customer)
            saved.refresh_from_db()
    else:
        try:
            saved = apmodels.SavedProduct.objects.get(session = request.session.session_key)
        except ObjectDoesNotExist:
            saved  = apmodels.SavedProduct.objects.create(session = request.session.session_key)
            saved.refresh_from_db()
    allObject['saved'] = saved or None
    saved_products = saved.products.all()
    allObject['products'] = saved_products
    allObject['paginatedproducts'] = str(request.path)
    allObject['session'] ='saved-items'

    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def categoryproducts(request,name=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    category = apmodels.Category.objects.get(name=name)
    products = list(category.products.all())
    products.sort(key=lambda x:x.date_time_added,reverse=True)
    # for product in products:
    #     product.save()
    allObject['products'] = products[0:12]
    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def homegrouppage(request,slug=None, *args, **kwargs):
    

    logrequest(request,'')

    allObject = inherit(request, *args, **kwargs)
    homegroup = apmodels.HomePageGroup.objects.get(slug=slug)
    products = list(homegroup.products.all())
    products.sort(key=lambda x:x.date_time_added,reverse=True)
    allObject['products'] = products
    allObject['section'] =homegroup.slug
    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def product_details(request,productid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/product_details.html'
    product = apmodels.Product.objects.get(productid=productid)
    product.view_count +=1
    product.save()
    productimages = apmodels.ProductImage.objects.filter(product=product)
    allObject['productimages'] = productimages
    flashsales = apmodels.FlashSale.objects.filter(end_date_time__gte =datetime.datetime.now(),start_date_time__lte=datetime.datetime.now())
    # allObject['store'] = store
    for flashsale in flashsales:
        for flashsaleproduct in flashsale.products.all():
            if product == flashsaleproduct.product:
                allObject['flashsaleproduct'] = flashsaleproduct
                break
    # customer = allObject['customer']
    allObject['title']= product.name + ' | Intelbyt'
    allObject['page'] = 'Product'
    allObject['product'] = product
    variations = list(product.variations.all())
    variations.sort(key=lambda x:x.price,reverse=False)
    if variations:
        allObject['variations'] =variations[0]
    slideshows = apmodels.SlideShow.objects.all()
    allObject['slideshows'] = slideshows
    return render(request,template_name,allObject)



def cart_count(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    homegroups = list(apmodels.HomePageGroup.objects.all())
    homegroups.sort(key=lambda x: x.index)
    allObject['homegroups'] = homegroups
    content_template = 'app/templates/home_group_container.html'
    allObject['section'] = 'home-group-sections'
    allObject['paginatedproducts'] = str(request.path)
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 



def products_you_may_like(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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
    content_template = 'app/templates/products.html'
    allObject['section'] = 'products-you-may-like'
    allObject['paginatedproducts'] = str(request.path)
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def topcategories(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    categories = list(apmodels.Category.objects.filter(is_top=True))
   
    content_template = 'app/templates/top_categories.html'
    allObject['topcategories'] = categories
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def similarproducts(request,productid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    product = apmodels.Product.objects.get(productid=productid)
    tags = product.tags.all()
    similar_products = apmodels.Product.objects.filter(tags__in=tags).distinct().exclude(productid=product.productid)

    # for product in products:
  
    allObject['products'] = similar_products
    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

def allproducts(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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
    allObject['section']='all-products'
    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def homegroupproducts(request,id=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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

    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def handler500(request, *args, **kwargs):

    return redirect('customer_error_500')

def handler404(request, *args, **kwargs):

    return redirect('customer_error_404')


def error500page(request, *args, **kwargs):

    allObject ={}
    try:
        store = list(admodels.General.objects.all())[0]
    except IndexError:
        store =[]    
    allObject['store'] = store
    allObject['server_timestamp'] = round(datetime.datetime.now().timestamp())
    allObject['title'] = 'Internal server error'

    if request.user.is_anonymous:
        pass
    else:
        user = User.objects.get(pk=request.user.pk)

    if request.user.is_authenticated:
        if user.is_superuser:
            pass
        else:
            try:
                current_user = apmodels.Customer.objects.get(user=user.pk)

                allObject['user'] = user
                allObject['customer'] = current_user
                customer = allObject['customer']      
            except ObjectDoesNotExist:
                pass        
            customer = allObject['customer']
            try:
                orders = apmodels.Order.objects.filter(customer = customer,deleted=False)
                allObject['orders'] = orders

            except ObjectDoesNotExist:
                pass
            try:
                saved = apmodels.SavedProduct.objects.get(customer = customer,)
                allObject['saved'] = len(saved.products.all()) or 0
            except ObjectDoesNotExist:
                pass
    else:
        try:
            orders = apmodels.Order.objects.filter(session = request.session.session_key,)
            allObject['orders'] = orders

        except ObjectDoesNotExist:
            pass
        try:
            saved = apmodels.SavedProduct.objects.get(session = request.session.session_key,)
            allObject['saved'] = len(saved.products.all()) or 0

        except ObjectDoesNotExist:
            pass
       
    socialoplatforms = admodels.SocialLink.objects.all()
    # allObject['socialmediaplatforms'] = socialoplatforms
    productgroups = apmodels.Category.objects.all()
    allObject['groupproducts'] = productgroups

    content_template = 'app/templates/500.html'
    content = loader.render_to_string(content_template,allObject,request)
    return render(request,content_template,allObject)


def error404page(request, *args, **kwargs):
    allObject ={}
    try:
        store = list(admodels.General.objects.all())[0]
    except IndexError:
        store =[]    
    allObject['store'] = store
    allObject['server_timestamp'] = round(datetime.datetime.now().timestamp())
    if request.user.is_anonymous:
        pass
    else:
        user = User.objects.get(pk=request.user.pk)

    if request.user.is_authenticated:
        if user.is_superuser:
            pass
        else:
            try:
                current_user = apmodels.Customer.objects.get(user=user.pk)

                allObject['user'] = user
                allObject['customer'] = current_user
                customer = allObject['customer']      
            except ObjectDoesNotExist:
                pass        
            customer = allObject['customer']
            try:
                orders = apmodels.Order.objects.filter(customer = customer,deleted=False)
                allObject['orders'] = orders

            except ObjectDoesNotExist:
                pass
            try:
                saved = apmodels.SavedProduct.objects.get(customer = customer,)
                allObject['saved'] = len(saved.products.all()) or 0
            except ObjectDoesNotExist:
                pass
    else:
        try:
            orders = apmodels.Order.objects.filter(session = request.session.session_key,)
            allObject['orders'] = orders

        except ObjectDoesNotExist:
            pass
        try:
            saved = apmodels.SavedProduct.objects.get(session = request.session.session_key,)
            allObject['saved'] = len(saved.products.all()) or 0

        except ObjectDoesNotExist:
            pass
       
    socialplatforms = admodels.SocialLink.objects.all()
    allObject['socialmediaplatforms'] = socialplatforms
    productgroups = apmodels.Category.objects.all()
    allObject['groupproducts'] = productgroups

    allObject['title'] = 'Content not found'
    content_template = 'app/templates/404.html'
    content = loader.render_to_string(content_template,allObject,request)
    return render(request,content_template,allObject)


def allhomegroupproducts(request,slug=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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

    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def newproducts(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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

    content_template = 'app/templates/new_products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def allflashsaleproducts(request,id=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    allproducts = apmodels.FlashSale.objects.get(pk=id).products.all()
    # for product in products:
    #     product.save()
    products = []
    for product in allproducts:
        products.append(product.product)
    page = request.GET.get('page', 1)

    paginator = Paginator(products, 10)
    try:
        pagproducts = paginator.page(page)
    except PageNotAnInteger:
        pagproducts = paginator.page(1)
    except EmptyPage:
        pagproducts = paginator.page(paginator.num_pages)
    allObject['products'] = pagproducts
    allObject['paginatedproducts'] = str(request.path)

    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

def flashsaleproducts(request,id=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    allproducts = apmodels.FlashSale.objects.get(pk=id).products.all()[:10]
    # for product in products:
    #     product.save()
    products = []
    for product in allproducts:
        products.append(product.product)
    page = request.GET.get('page', 1)

    paginator = Paginator(products, 10)
    try:
        pagproducts = paginator.page(page)
    except PageNotAnInteger:
        pagproducts = paginator.page(1)
    except EmptyPage:
        pagproducts = paginator.page(paginator.num_pages)
    allObject['products'] = pagproducts
    allObject['paginatedproducts'] = str(request.path)

    content_template = 'app/templates/products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def flashsaleproduct(request,id=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    product = apmodels.FlashSaleProduct.objects.get(pk=id)
    productimages = apmodels.ProductImage.objects.filter(product=product.product)
    allObject['productimages'] = productimages
    allObject['product'] = product
    content_template = 'app/templates/flash_sale_product.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def product(request,id=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    if request.user.is_authenticated:
        if request.user.is_superuser:
            pass
        else:
            customer = allObject['customer']
            try:
                    saved = apmodels.SavedProduct.objects.get(customer = customer,)
                    allObject['saved'] = saved
            except ObjectDoesNotExist:
                pass
    else:

        try:
            saved = apmodels.SavedProduct.objects.get(session = request.session.session_key,)
            allObject['saved'] = saved
        except ObjectDoesNotExist:
            pass
    product = apmodels.Product.objects.get(pk=id)
    productimages = apmodels.ProductImage.objects.filter(product=product,flip=True)
    try:
        allObject['flipimage'] = productimages[0]
    except Exception:
        pass
    allObject['product'] = product
    content_template = 'app/templates/product.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def cartedproduct(request,id=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    cartedproduct = apmodels.CartedProduct.objects.get(cartedproductid=id)
    flashsales = apmodels.FlashSale.objects.filter(end_date_time__gte =datetime.datetime.now(),start_date_time__lte=datetime.datetime.now())
    for flashsale in flashsales:
        for flashsaleproduct in flashsale.products.all():
            if cartedproduct.product == flashsaleproduct.product:
                allObject['flashsaleproduct'] = flashsaleproduct
                break

    allObject['product'] = cartedproduct
    content_template = 'app/templates/carted_product.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def slideshows(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    allslideshows = list(apmodels.SlideShow.objects.all())
    # for product in products:
    #     product.save()

    allObject['slideshows'] = allslideshows
    content_template = 'app/templates/slideshows.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 

def paginatedproducts(request,productid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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

    content_template = 'app/templates/paginated_products.html'
    content = loader.render_to_string(content_template,allObject,request)
    output_data = {
    'content': content,
                    }
    return JsonResponse(output_data) 


def place_order(request,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    customer = allObject['customer']
    if request.method == 'POST':
        delivery = str(request.POST.copy().get('delivery'))
        location = str(request.POST.copy().get('location'))
        if delivery != 'p':
            if customer.contact_ready:
                pass
            else:
                content_template = 'app/templates/contact_form.html'
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
            order = apmodels.Order.objects.create(customer=customer,)
            for product in cart.products.all():

                order.products.add(product)
            order.save()

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
        print("cart cleared")

        allObject['order'] = order
        content_template = 'app/templates/order_placed.html'
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
    allObject = inherit(request, *args, **kwargs)
    # customer = allObject['customer']
    # products = apmodels.CartedProduct.objects.all()

    # for product in products:
    #     product.delete()
    # return True
    
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
    print('here')
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
    # cart.products.clear()

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
    allObject = inherit(request, *args, **kwargs)
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
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,ordered=False,variation__id=variationid, customer=customer)
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
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,ordered=False,variation__id=variationid, session = request.session.session_key)
                else:
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,ordered=False, session = request.session.session_key)

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
                flashsales = apmodels.FlashSale.objects.filter(end_date_time__gte =datetime.datetime.now(),start_date_time__lte=datetime.datetime.now())
                for flashsale in flashsales:
                    for flashsaleproduct in flashsale.products.all():
                        if product == flashsaleproduct.product:
                            allObject['flashsaleproduct'] = flashsaleproduct
                            break
                content_template = 'app/templates/cart_form_modal.html'
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
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,ordered=False, customer=customer)

                except ObjectDoesNotExist:

                    cartedproduct = apmodels.CartedProduct.objects.create(product=product,ordered=False, customer=customer,quantity = 1)
            
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
            'containers':['cart-container','cart-count']
                            }
            return JsonResponse(output_data)

def add_variation_to_cart(request,productid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    customer = False
 
    if request.method == 'POST':
        variationid = str(request.POST.copy().get('variationid'))
        productid = str(request.POST.copy().get('productid'))
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
                    cartedproduct = apmodels.CartedProduct.objects.get(product=product,ordered=False,variation__id=variationid, customer=customer)
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
        cart.refresh_from_db()

        output_data = {
        'notification': 'Product added to cart',
        'loadcontent':True,
        'reload_url':redirect('customer_cart_count').url,
        'container':['cart-count']
                        }
        return JsonResponse(output_data) 
    else:
       
        output_data = {
        'notification': 'Invalid request',
                        }
        return JsonResponse(output_data) 


def add_to_saved(request,productid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    customer = False
    product = apmodels.Product.objects.get(productid=productid)

    if request.user.is_authenticated:
        customer = allObject['customer']
        try:
            saved = apmodels.SavedProduct.objects.get(customer = customer)
        except ObjectDoesNotExist:
            saved  = apmodels.SavedProduct.objects.create(customer=customer)
            saved.refresh_from_db()

    else:
        try:
            saved = apmodels.SavedProduct.objects.get(session = request.session.session_key)

        except ObjectDoesNotExist:
            saved  = apmodels.SavedProduct.objects.create(session=request.session.session_key)
            saved.refresh_from_db()
    if product in saved.products.all():
        output_data = {
        'content': saved.products.all().count(),
        'notification': 'Product already saved',
                        }
    else:
        saved.products.add(product)

        allObject['product'] = product
        add_to_saved_button = 'app/templates/remove_from_saved_button.html'
        content = loader.render_to_string(add_to_saved_button,allObject,request)
        output_data = {
            'content':content,
        'notification': 'Product saved',
                        }
    return JsonResponse(output_data) 

def remove_from_saved(request,productid=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    customer = False
    product = apmodels.Product.objects.get(productid=productid)

    if request.user.is_authenticated:
        if request.user.is_superuser:
            try:
                saved = apmodels.SavedProduct.objects.get(session = request.session.session_key)

            except ObjectDoesNotExist:
                saved  = apmodels.SavedProduct.objects.create(session=request.session.session_key)
                saved.refresh_from_db()
        else:
            customer = allObject['customer']
            try:
                saved = apmodels.SavedProduct.objects.get(customer = customer)
            except ObjectDoesNotExist:
                saved  = apmodels.SavedProduct.objects.create(customer=customer)
                saved.refresh_from_db()

    else:
        try:
            saved = apmodels.SavedProduct.objects.get(session = request.session.session_key)

        except ObjectDoesNotExist:
            saved  = apmodels.SavedProduct.objects.create(session=request.session.session_key)
            saved.refresh_from_db()
    if product in saved.products.all():
        saved.products.remove(product)
        allObject['product'] = product
        add_to_saved_button = 'app/templates/add_to_saved_button.html'
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


@customer_login_required
def checkout(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    if request.method == 'POST':
        customer = allObject['customer']
        try:
            cart = apmodels.Cart.objects.get(customer = customer)
        except ObjectDoesNotExist:
            pass
        try:
            order = apmodels.Order.objects.get(customer=customer,complete = False)
        except ObjectDoesNotExist:
            order = apmodels.Order.objects.get(customer=customer)

        # else:
        #     try:
        #         cart = apmodels.Cart.objects.get(session = request.session.session_key)

        #     except ObjectDoesNotExist:
        #         cart  = apmodels.Cart.objects.create(session=request.session.session_key)
        #         cart.refresh_from_db()
        #     try:
        #         cartedproduct = apmodels.CartedProduct.objects.get(product=product, session = request.session.session_key)

        #     except ObjectDoesNotExist:
        #         cartedproduct = apmodels.CartedProduct.objects.create(product=product, session=request.session.session_key,quantity = quantity)
    
        cartedproduct.quantity = quantity
        cartedproduct.save()        
        cart.products.add(cartedproduct)

        allObject['message'] = '<span class="text-primary uk-text-bold h1">Product added to cart </span>'
        message_template = 'general/success.html'
        global message
        message = loader.render_to_string(message_template,allObject,request)
        cart.refresh_from_db()
    else:
        template_name = 'app/templates/checkout.html'
        # customer = allObject['customer']
        allObject['title']='Checkout | Intelbyt'
        # if request.user.is_authenticated:
        customer = allObject['customer']
        cart = apmodels.Cart.objects.get(customer = customer)
        # else:
        #     cart = apmodels.Cart.objects.get(session = request.session.session_key)
        # for product in cart.products.all():
        #     product.save()
        cart.save()
        allObject['cart'] = cart or None
        locations = apmodels.DeliveryLocation.objects.all()
        allObject['locations'] = locations

        return render(request,template_name,allObject)




def remove_from_cart(request,id=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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

    # allObject['cart'] = cart
    # content_template = 'app/templates/cart_container.html'
    # content = loader.render_to_string(content_template,allObject,request)

    output_data = {
    'loadcontent':True,
    'reload_url':redirect('customer_cart_count').url,
    'containers':['cart-count','cart-container'],
    'notification':'Product removed from cart'
                    }
    return JsonResponse(output_data) 





@customer_login_required
def dashboard(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/dashboard.html'
    customer = allObject['customer']
    allObject['title']='DPG | Dashboard'
    allObject['page'] = 'Dashboard'
    # customer.privacy_terms_accepted = True
    # customer.save()
    # for i in range(10):
    #     apmodels.CreditPin.objects.create(amount=200)
    customerstatus = checkcustomerstatus(request, customer)
    if type(customerstatus) == bool:
        # payments=list(pmodels.Payment.objects.filter(customer=customer,approved=True))
        # payments.sort(key =lambda x:x.date_time_added,reverse=True)
        # allObject['payments'] = payments
        # try:
        # allObject['monthlypayments'] = allObject['monthlypayments'][0:5]
        # allObject['pendingupdates'] = allObject['pendingupdates'][0:5]
        # except KeyError:
        #     pass
        # if customer.active_loan:
        #     try:
        #         activelaon = apmodels.Loan.objects.get(customer=customer,repaid=False)
        #         activelaon.save()
        #         allObject['activeloan'] = activelaon
        #     except ObjectDoesNotExist:
        #         pass
        return render(request,template_name,allObject)
    else:
        return customerstatus




def downloadorder(request,orderid=None,*args, **kwargs):
    allObject = inherit(request, *args, **kwargs)

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
    template_name = 'app/templates/order_download.html'
    response = PDFTemplateResponse(request=request,
                                    template='app/templates/order_download.html',
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
    allObject = inherit(request, *args, **kwargs)
    template_name = 'app/templates/my_order.html'
    # customer = allObject['customer']
    allObject['title']='My Order | Intelbyt'
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
    allObject = inherit(request, *args, **kwargs)
    customer = allObject['customer']
    if request.method == 'POST':
        orderid = request.POST.copy().get('orderid')
        order = apmodels.Order.objects.get(orderid=orderid)
        order.payment_method = 'op'
        order.paid=True
        order.date_time_paid =datetime.datetime.now()
        order.save()
        for product in order.products.all():
            product.paid = True
            product.ordered= True
            product.date_time_paid = datetime.datetime.now()
            product.save()
            product.product.purchase_count +=product.quantity
            product.product.save()
            store = smodels.Store.objects.filter(products=product.product)[0]
            store.orders.add(product)
            # orders = apmodels.Order.objects.filter(customer=customer,)

        subject = 'New Order Placed - '+order.orderid

        message = render_to_string('app/templates/order_placed_email.html', {
                'order':order,
                'customer':customer,
            'title':'ORDER PLACED',
            'socials':admodels.SocialLink.objects.all(),
            'store':allObject['store']
            })
        recipient_list = [allObject['store'].email, ]
        to = recipient_list
        subject = subject
        body = message
        sendmail(to,body,body,subject)
        subject = 'New Order Placed - '+order.orderid

        message = render_to_string('app/templates/customer_order_placed_email.html', {
                'order':order,
                'customer':customer,
                'title':'ORDER PLACED',
                'socials':admodels.SocialLink.objects.all(),
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
    allObject = inherit(request, *args, **kwargs)
    customer = allObject['customer']
    order = apmodels.Order.objects.get(orderid=orderid)
    order.payment_method = 'pd'
    # order.paid=True
    # order.date_time_paid =datetime.datetime.now()
    order.save()
    # orders = apmodels.Order.objects.filter(customer=customer,)
    order.refresh_from_db()
    for product in order.products.all():
        product.product.purchase_count +=product.quantity
        product.ordered= True
        product.save()
        store = smodels.Store.objects.filter(products=product.product)[0]
        store.orders.add(product)
        product.product.save()
    subject = 'New Order Placed - '+order.orderid

    message = render_to_string('app/templates/order_placed_email.html', {
            'order':order,
            'customer':customer,
            'title':'ORDER PLACED',
            'socials':admodels.SocialLink.objects.all(),
            'store':allObject['store']
        })
    recipient_list = [allObject['store'].email, ]
    to = recipient_list
    subject = subject
    body = message
    sendmail(to,body,body,subject)

    subject = 'New Order Placed - '+order.orderid

    message = render_to_string('app/templates/customer_order_placed_email.html', {
            'order':order,
            'customer':customer,
            'title':'ORDER PLACED',
            'socials':admodels.SocialLink.objects.all(),
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
   


@customer_login_required
def investmentsuccessful(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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




@customer_login_required
def investmentbrief(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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
    template_name = 'app/templates/investment_brief.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
    'details':content,
                    }
    return JsonResponse(output_data)



@customer_login_required
def checkfetchaccountnumber(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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


@customer_login_required
def checkaccountnumber(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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


@customer_login_required
def directqrccredit(request,pin, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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



@customer_login_required
@sufficientbalance
def generatepinqrcode(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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

        template_name = 'app/templates/qrcode_response.html'
        allObject['qrc_options'] =QRCodeOptions(qrtext,custom_text=qrtext, size='18', border=8, error_correction='L',image_format='png')
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                'full_modal':content,  
                        }
        return JsonResponse(output_data) 

@customer_login_required
def creditmodalcontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    customer = allObject['customer']
    account_number = customer.savings_account.number
    allObject['qrc_options'] =QRCodeOptions(account_number,custom_text=account_number, size='10', border=8, error_correction='L',image_format='png')

    template_name = 'app/templates/credit_modal_content.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
                        'content':content,
                    }
    return JsonResponse(output_data)


@customer_login_required
def share(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    customer = allObject['customer']

    template_name = 'app/templates/share_form.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
                        'content':content,
                        'title':'Fetch Share'
                    }
    return JsonResponse(output_data)


@customer_login_required
@sufficientbalance
def withdraw(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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
            template_name = 'app/templates/withdrawal_form.html'
        except ObjectDoesNotExist:
            bank = apmodels.Bank.objects.get(name='Gtbank')
            allObject['bank']=bank
            template_name = 'app/templates/no_account.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Fetch Withdrawal'
                        }
        return JsonResponse(output_data)




@customer_login_required
def verifydeposit(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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




@customer_login_required
def verifyinvestment(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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



@customer_login_required
def deposit(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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

        template_name = 'app/templates/deposit_form.html'
        
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Fetch Deposit'
                        }
        return JsonResponse(output_data)


@customer_login_required
def invest(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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

        template_name = 'app/templates/invest_form.html'
        
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Fetch Invest'
                        }
        return JsonResponse(output_data)


@customer_login_required
def addaccount(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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
        template_name = 'app/templates/add_account_form.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Add Account Number'
                        }
        return JsonResponse(output_data)



@customer_login_required
def choosetransferdestination(request,destination=None, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    customer = allObject['customer']
    template_name = 'app/templates/choose_transfer_destination.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
                        'content':content,
                        'title':'Choose destination'
                    }
    return JsonResponse(output_data)




@customer_login_required
@sufficientbalance
def internaltransfer(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
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
        template_name = 'app/templates/internal_transfer_form.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Transfer to Fetch account'
                        }
        return JsonResponse(output_data)



@customer_login_required
@sufficientbalance
def externaltransfer(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    customer = allObject['customer']

    if request.method =='POST':
        bank_code = request.POST.copy().get('bank')
        amount =int(request.POST.copy().get('amount'))
        account_number = request.POST.copy().get('account_number')
        bank = apmodels.Bank.objects.get(code=bank_code)
        transfer = apmodels.TransferTransaction.objects.create(customer=customer, amount=amount,bank=bank,account_number=account_number)
        transfer.refresh_from_db()
        debitaccount(request,customer,transfer.amount)
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
        template_name = 'app/templates/external_transfer_form.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                            'title':'Transfer to other banks'
                        }
        return JsonResponse(output_data)





def customerlookup(request, *args, **kwargs):
    # auth.logout(request)
    # if request.user.is_authenticated:
    #     logout(request)
    #     return redirect('account_login')
    allObject = inherit(request, *args, **kwargs)
    allObject['title']='Login | Intelbyt'
    seller = False
    if request.method == 'POST':

        uniqueidentifier = request.POST.copy().get('identifier').lower()
        try:
            user = User.objects.get(username = uniqueidentifier)
            # profile = apmodels.Customer.objects.filter(phone_number_1=uniqueidentifier)[0]
        except ObjectDoesNotExist:
            try:
                user = User.objects.get(email = uniqueidentifier)
                # profile = apmodels.Customer.objects.get(email=uniqueidentifier)
            except ObjectDoesNotExist:
                # try:
                #     profile = apmodels.Customer.objects.filter(phone_number_2=uniqueidentifier)[0]
                # except Exception:
                #     try:
                #         seller = User.objects.get(username = uniqueidentifier)
                #         seller= True

                output_data = {
                    'invalid':True,
                    'error':'Record not found.'
                }
                return JsonResponse(output_data)
        # if not seller:
        #     try:
        #         user = User.objects.get(pk=profile.user.pk)
        #     except ObjectDoesNotExist:
        #         allObject['identifier']=uniqueidentifier
        #         allObject['profile']=profile

        #         allObject['profile']=profile
        #         template_name = 'allauth/account/create_password.html'
        #         content = loader.render_to_string(template_name,allObject,request)
        #         output_data = {
        #                     'form_content':content,
        #                 }
        #         return JsonResponse(output_data)

        if request.POST.copy().get('next'):
            allObject['next_page']=request.POST.copy().get('next')
            allObject['redirect_url']=''.join(tuple(request.POST.copy().get('next')))
        allObject['identifier']=uniqueidentifier

        template_name = 'allauth/account/enter_password.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                    'form_content':content,
                }
        return JsonResponse(output_data)
        login(request, user)   
        customer = True
        allObject = inherit(request)
        customer = apmodels.customer.objects.get(user=user,dependant=False)
        customer = True
        template_name = 'customers/dashboard.html'
        content = loader.render_to_string(template_name,allObject,request)
        if request.POST.copy().get('next'):
                redirectinstance= redirect(request.POST.copy().get('next'))
        output_data = {
                            'logged_in':True,
                            'url':redirectinstance.url
                        }
        return JsonResponse(output_data)



    else:
        form = allauthforms.LoginForm()
        allObject['form'] = form
        if request.GET.get('next'):
            allObject['next_page']=request.GET.get('next')
            allObject['redirect_url']=''.join(tuple(request.GET.get('next')))
        template_name = 'allauth/account/customer_lookup.html'
        return render(request,template_name,allObject)
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                        }
        return JsonResponse(output_data)



def customersignup(request, *args, **kwargs):
    allObject = inherit(request)
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
        # form.user_id = user_id
        exist = True
        while exist:
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
            firstletter= user.first_name[0].upper()
            lastletter =user.last_name[0].upper()
            temporary_userid = tempnums[0:3] + templalph[0:3]+tempualph[0:3]+firstletter+lastletter
            userid= []
            for char in temporary_userid:
                userid.insert(round(random()*5),char)
            userid = ''.join(userid)
            userid = 'D'+userid

            try:                
                apmodels.Customer.objects.get(customerid=userid)

            except ObjectDoesNotExist:

                apmodels.Customer.objects.create(user=user,customerid=userid,last_token=make_password(token),
                last_name=last_name,email=email or 'none', first_name=first_name,)
                exist = False
                break

        user.is_active = True
        user.save()
        try:
            cart = apmodels.Cart.objects.get(session = request.session.session_key)
        except ObjectDoesNotExist:
            cart =[]
        try:
            orders = apmodels.Order.objects.filter(session = request.session.session_key)
        except ObjectDoesNotExist:
            orders =[]

        if user:
            customer=apmodels.Customer.objects.get(user=user)
            try:
                if len(cart.products.all()) > 0:
                    try:
                        newcart  = apmodels.Cart.objects.get(customer=customer)
                    except ObjectDoesNotExist:
                        newcart  = apmodels.Cart.objects.create(session='',customer=customer)
                    newcart.refresh_from_db()
                    for product in cart.products.all():
                        newcart.products.add(product)
                        product.customer = customer
                    cart.delete()
                
            except AttributeError:
                pass

            if orders:
                for order in orders:
                    order.customer= customer
                    order.save()
            

       
        login(request, user)
        allObject = inherit(request)
        if request.POST.copy().get('next'):
            redirectinstance= redirect(request.POST.copy().get('next'))
            redirecturl = redirectinstance.url
        else:
            if user.is_superuser:
                redirecturl = redirect('seller_dashboard').url
            else:
                redirecturl = redirect('customer_home').url
        output_data = {
                            'logged_in':True,
                            'url':redirecturl
                        }
        return JsonResponse(output_data)

  
    else:
        form = allauthforms.LoginForm()
        allObject['form'] = form
        print('cool')
        if request.GET.get('next'):
            allObject['next_page']=request.GET.get('next')
            allObject['redirect_url']=''.join(tuple(request.GET.get('next')))
        template_name = 'allauth/account/customer_signup.html'
        nexturl = redirect('customer_home').url

        if request.GET.get('next'):
            nexturl =str(request.GET.get('next'))
        # return render(request,template_name,allObject)
        allObject['nexturl'] = nexturl
        content = loader.render_to_string(template_name,allObject,request)

        # if inline:

        #     return True

        return render(request,template_name,allObject)


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
        if user.is_superuser:
            pass
        else:
            try:
                cart = apmodels.Cart.objects.get(session = request.session.session_key)
            except ObjectDoesNotExist:
                cart =[]
            try:
                orders = apmodels.Order.objects.filter(session = request.session.session_key)
            except ObjectDoesNotExist:
                orders =[]
            try:
                saved = apmodels.SavedProduct.objects.get(session = request.session.session_key)
            except ObjectDoesNotExist:
                saved =[]

        if user:
            if user.is_superuser:
                pass
            else:

                customer=apmodels.Customer.objects.get(user=userObject)
                logrequest(request,customer.customerid or '')

                if saved:
                    try:
                        alreadysaved = apmodels.SavedProduct.objects.get(customer=customer)
                        for product in saved.products.all():
                            if product not in alreadysaved.products.all():
                                alreadysaved.products.add(product)
                    except ObjectDoesNotExist:    
                        saved.customer=customer
                        saved.save()
                try:
                    if len(cart.products.all()) > 0:
                        try:
                            newcart  = apmodels.Cart.objects.get(customer=customer)
                        except ObjectDoesNotExist:
                            newcart  = apmodels.Cart.objects.create(session='',customer=customer)
                        newcart.refresh_from_db()
                        newcartproducts =[]
                        for newcartproduct in newcart.products.all():
                            newcartproducts.append(newcartproduct.product)
                        for product in cart.products.all():
                            if product.product in newcartproducts:
                                pass
                                
                            else:
                                newcart.products.add(product)
                        product.customer = customer
                        cart.delete()
                    
                except AttributeError:
                    pass

                if orders:
                    for order in orders:
                        order.customer= customer
                        order.save()


            login(request, user)
        else:
            output_data = {
            'invalid':True,
            'modal_notification':'Invalid password'
                }
            return JsonResponse(output_data)
        # allObject = inherit(request)
        # template_name = 'customers/dashboard.html'
        # content = loader.render_to_string(template_name,allObject,request)
        if request.POST.copy().get('next'):
                redirectinstance= redirect(request.POST.copy().get('next'))
                redirecturl = redirectinstance.url
        else:
            redirecturl = redirect('customer_home').url
        output_data = {
                            'logged_in':True,
                            'url':redirecturl
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


def signup(request, *args, **kwargs):
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
        # form.user_id = user_id
        exist = True
        while exist:
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
            firstletter= user.first_name[0].upper()
            lastletter =user.last_name[0].upper()
            temporary_userid = tempnums[0:3] + templalph[0:3]+tempualph[0:3]+firstletter+lastletter
            userid= []
            for char in temporary_userid:
                userid.insert(round(random()*5),char)
            userid = ''.join(userid)
            userid = 'D'+userid

            try:                
                apmodels.Customer.objects.get(customerid=userid)

            except ObjectDoesNotExist:

                apmodels.Customer.objects.create(user=user,customerid=userid,last_token=make_password(token),
                last_name=last_name,email=email or 'none', first_name=first_name,)
                exist = False
                break

        user.is_active = True
        user.save()
        try:
            cart = apmodels.Cart.objects.get(session = request.session.session_key)
        except ObjectDoesNotExist:
            cart =[]
        try:
            orders = apmodels.Order.objects.filter(session = request.session.session_key)
        except ObjectDoesNotExist:
            orders =[]

        if user:
            customer=apmodels.Customer.objects.get(user=user)
            try:
                if len(cart.products.all()) > 0:
                    try:
                        newcart  = apmodels.Cart.objects.get(customer=customer)
                    except ObjectDoesNotExist:
                        newcart  = apmodels.Cart.objects.create(session='',customer=customer)
                    newcart.refresh_from_db()
                    for product in cart.products.all():
                        newcart.products.add(product)
                        product.customer = customer
                    cart.delete()
                
            except AttributeError:
                pass

            if orders:
                for order in orders:
                    order.customer= customer
                    order.save()
            

       
        login(request, user)
        allObject = inherit(request)
        if request.POST.copy().get('next'):
            redirectinstance= redirect(request.POST.copy().get('next'))
            redirecturl = redirectinstance.url
        else:
            if user.is_superuser:
                redirecturl = redirect('seller_dashboard').url
            else:
                redirecturl = redirect('customer_home').url
        output_data = {
                            'logged_in':True,
                            'url':redirecturl
                        }
        return JsonResponse(output_data)
    else:
        form = gforms.SignUpForm()
        allObject = inherit(request, *args, **kwargs)
        allObject['form'] = form
        return render(request, 'allauth/account/signup.html', allObject)



def logoutuser(request, *args, **kwargs):
    try:
        cart = apmodels.Cart.objects.get(session = request.session.session_key)
    except ObjectDoesNotExist:
        cart =[]
    try:
        orders = apmodels.Order.objects.filter(session = request.session.session_key)
    except ObjectDoesNotExist:
        orders =[]
    try:
        saved = apmodels.SavedProduct.objects.get(session = request.session.session_key)
    except ObjectDoesNotExist:
        saved =[]
    auth.logout(request)
    print("Session key is  "+request.session['session_key'])
    form = allauthforms.LoginForm()
    allObject = inherit(request, *args, **kwargs)
    if cart:
        cart.session =  request.session.session_key
        cart.save()

    if saved:
        saved.session= request.session.session_key
        saved.save()
    if orders:
        for order in orders:
            order.session =  request.session.session_key
            order.save()
    allObject['form'] = form
    template_name = 'allauth/account/login.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
                        'content':content,
                    }
    return redirect('customer_home')

