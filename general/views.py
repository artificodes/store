from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.shortcuts import render, redirect
from allauth.account.views import SignupView
import app

from django.core.exceptions import ObjectDoesNotExist
from general import models as gmodels
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
import datetime
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
allObject = {}


def inherit(request, *args, **kwargs):
    allObject={}
    try:
        settings = list(gmodels.General.objects.all())[0]
    except IndexError:
        settings =[]
    allObject['settings'] = settings
    allObject['server_timestamp'] = round(datetime.datetime.now().timestamp())
    return allObject


def app(request, *args, **kwargs):
    allObject = inherit(request)
    template_name = 'base/app.html'
    store = allObject['store']
    try:
        allObject['title']=store.store_name
    except Exception:
        allObject['title']='Welcome . Intelbyt'
    content = loader.render_to_string(template_name,allObject,request)
    nexturl = '/dashboard'
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


def gallery(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/gallery.html'
    page = request.GET.get('page', 1)

    allObject['page'] = page
    content = loader.render_to_string(template_name,allObject,request)
    template_name = 'frontend/gallery.html'
    return render(request,template_name,allObject)



def gallerycontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/gallery_content.html'
    gallery = list(gmodels.Gallery.objects.all())
    gallery.sort(key=lambda x: x.date_time_added,reverse=True)
    page = request.GET.get('page')
    paginator = Paginator(gallery, 8)
    try:
        gallery = paginator.get_page(page)
    except PageNotAnInteger:
        gallery = paginator.get_page(1)
    except EmptyPage:
        gallery = paginator.get_page(paginator.num_pages)
    allObject['gallery'] = gallery

    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)

def momentoftruth(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/moment_of_truth.html'
    content = loader.render_to_string(template_name,allObject,request)
    return render(request,template_name,allObject)


def momentoftruthcontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/moment_of_truth_content.html'
    tvs = list(apmodels.TvStation.objects.all())
    allObject['tvs'] = tvs
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)



def upcomingevents(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/upcoming_events.html'
    content = loader.render_to_string(template_name,allObject,request)
    return render(request,template_name,allObject)


def upcomingeventscontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/upcoming_events_content.html'
    upcomingevents = list(apmodels.Event.objects.all())
    upcomingevents =  list(apmodels.Event.objects.filter(start_date_time__gt = datetime.datetime.now()))
    allObject['upcomingevents'] =upcomingevents    
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)





def pastevents(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/past_events.html'
    content = loader.render_to_string(template_name,allObject,request)
    return render(request,template_name,allObject)


def pasteventscontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/past_events_content.html'
    pastevents =  list(apmodels.Event.objects.filter(end_date_time__lt = datetime.datetime.now(),start_date_time__lt=datetime.datetime.now()))
    pastevents.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['pastevents'] =pastevents
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)





def videos(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/videos.html'
    content = loader.render_to_string(template_name,allObject,request)
    return render(request,template_name,allObject)


def videoscontent(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/videos_content.html'
    videos = list(apmodels.Video.objects.all())
    videos.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['latestvideo'] = videos[0]
    allObject['videos'] =videos
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)



def home(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    template_name = 'frontend/home.html'
    return render(request,template_name,allObject)

def slideshow(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    slideshows = gmodels.SlideShow.objects.all()
    allObject['slideshows'] = slideshows
    template_name = 'frontend/slideshow.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)



def galleryhome(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    gallery = list(gmodels.Gallery.objects.all())
    gallery.sort(key=lambda x: x.date_time_added,reverse=True)
    page = request.GET.get('page', 1)
    paginator = Paginator(gallery, 7)
    try:
        gallery = paginator.page(page)
    except PageNotAnInteger:
        gallery = paginator.page(1)
    except EmptyPage:
        gallery = paginator.page(paginator.num_pages)
    allObject['gallery'] = gallery
    template_name = 'frontend/home_gallery.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)


def sendmessage(request, *args, **kwargs):
    allObject= inherit(request, *args, **kwargs)
    if request.method == 'POST':
        newmessage = str(request.POST.copy().get('message'))
        fullname = str(request.POST.copy().get('name'))
        phonenumber = str(request.POST.copy().get('phonenumber'))
        email = str(request.POST.copy().get('email'))
        message = gmodels.ContactMessage.objects.create(name=fullname,email=email,number=phonenumber,message=newmessage)
        message.refresh_from_db()
        subject = 'New Message'
        current_site = Site.objects.get_current()


        email_from = settings.EMAIL_HOST_USER 
        recipient_list = [message.email, ] 
        message = render_to_string('frontend/new_message.html', {
                'message': message,
            })
        send_mail( subject, message, email_from, recipient_list ) 
        template_name = 'frontend/success.html'
        allObject['message'] = 'Your Message was sent successfully'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
            'sent':True,
            'content':content,
                            }
        return JsonResponse(output_data)


def kingdomstrategieshome(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    videos = list(apmodels.Video.objects.all())
    videos.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['latestvideo'] = videos[0]
    # allObject['videos'] =videos
    articles = list(apmodels.Article.objects.all())
    articles.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['latestarticle'] = articles[0]
    articles.remove(articles[0])
    allObject['articles'] =articles
    template_name = 'frontend/home_kingdom_strategies.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)


def events(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    upcomingevents =  list(apmodels.Event.objects.filter(start_date_time__gt = datetime.datetime.now()))
    upcomingevents.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['upcomingevents'] =upcomingevents
    pastevents =  list(apmodels.Event.objects.filter(end_date_time__lt = datetime.datetime.now(),start_date_time__lt=datetime.datetime.now()))
    pastevents.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['pastevents'] =pastevents
    template_name = 'frontend/events.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
        'content':content,
                        }
    return JsonResponse(output_data)



def pastorsdesk(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    pastorsdesk = list(gmodels.PastorsDesk.objects.all())[0]
    allObject['pastorsdesk'] = pastorsdesk

    template_name = 'frontend/pastors_desk.html'
    return render(request,template_name,allObject)


def contactus(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)

    template_name = 'frontend/contact.html'
    return render(request,template_name,allObject)


def kingdomstrategies(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    allObject['pastorsdesk'] = pastorsdesk
    videos = list(apmodels.Video.objects.all())
    videos.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['latestvideo'] = videos[0]
    videos.remove(videos[0])
    allObject['videos'] =videos
    articles = list(apmodels.Article.objects.all())
    articles.sort(key=lambda x: x.date_time_added,reverse=True)
    allObject['articles'] =articles
    template_name = 'frontend/kingdom_strategies.html'
    return render(request,template_name,allObject)



@login_required
def unsuspend(request, *args, **kwargs):
    user = User.objects.get(email=request.user.email)
    try:
        customer = apmodels.Customer.objects.get(user=user)
        customer.briefly_suspended = False
        customer.suspension_count =0
        customer.save()
        output_data = {
            'customer':True,
            'unsuspended':True,
                            }
        return JsonResponse(output_data)
    except ObjectDoesNotExist:
        customer = apmodels.Customer.objects.get(user=user)
        customer.briefly_suspended = False
        customer.suspension_count = 0
        customer.save()
        output_data = {
            'customer':True,
            'unsuspended':True,
                            }
        return JsonResponse(output_data)



# @login_required
# def home(request, *args, **kwargs):
#     user = User.objects.get(email=request.user.email).pk
#     try:
#         customer = apmodels.Customer.objects.get(user=user)
#         customer = True
#         return cviews.home(request, *args, **kwargs)
#     except ObjectDoesNotExist:
#         customer = apmodels.Customer.objects.get(user=user)
#         customer=True 
#         return cviews.home(request, *args, **kwargs)    




def customerlookup(request, *args, **kwargs):
    # auth.logout(request)
    # if request.user.is_authenticated:
    #     logout(request)
    #     return redirect('account_login')
    allObject = inherit(request, *args, **kwargs)
    allObject['title']=allObject['settings'].store_name +' | Login In'
    admin = False
    if request.method == 'POST':

        uniqueidentifier = request.POST.copy().get('identifier').lower()
        try:
            profile = apmodels.Customer.objects.filter(phone_number_1=uniqueidentifier)[0]
        except Exception:
            try:
                profile = apmodels.Customer.objects.get(email=uniqueidentifier)
            except ObjectDoesNotExist:
                try:
                    profile = apmodels.Customer.objects.filter(phone_number_2=uniqueidentifier)[0]
                except Exception:
                    try:
                        admin = User.objects.get(username = uniqueidentifier)
                        admin= True
                    except ObjectDoesNotExist:
                        output_data = {
                            'invalid':True,
                            'error':'Record not found.'
                        }
                        return JsonResponse(output_data)
        if not admin:
            try:
                user = User.objects.get(pk=profile.user.pk)
            except ObjectDoesNotExist:
                allObject['identifier']=uniqueidentifier
                allObject['profile']=profile

                allObject['profile']=profile
                template_name = 'allauth/account/create_password.html'
                content = loader.render_to_string(template_name,allObject,request)
                output_data = {
                            'form_content':content,
                        }
                return JsonResponse(output_data)

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
    if request.method == 'POST':
        uniqueidentifier = request.POST.copy().get('identifier').lower()
        password = request.POST.copy().get('password')
        try:
            profile = apmodels.Customer.objects.get(phone_no__contains=uniqueidentifier)
        except ObjectDoesNotExist:
            try:
                profile = apmodels.Customer.objects.get(email_addres=uniqueidentifier)
            except ObjectDoesNotExist:
                try:
                    profile = apmodels.Customer.objects.get(phone_no_alt__contains=uniqueidentifier)
                except ObjectDoesNotExist:
                    pass
        formerrors = []
        try:
            user= User.objects.get(username=uniqueidentifier)
            formerrors.append("<li class='text-sm uk-text-bold'>Username/Phone number already taken</li>")

        except ObjectDoesNotExist:
            try:
                user= User.objects.get(email=uniqueidentifier)
                formerrors.append("<li class='text-sm uk-text-bold'>Email already taken</li>")

            except ObjectDoesNotExist:
                pass
        if formerrors:
            erroroutput ="<ul class='text-danger p-0'>"
            errorlist = ''
            for error in formerrors:
                errorlist += '<li>' +str(error)+'</li>'
            erroroutput += errorlist + '</ul>'
            output_data = { 
                            'invalid':True,
                            'modal_notification':'<b>Ooops... Something is wrong!</b>' + erroroutput,
                            
                        }
            return JsonResponse(output_data)
        harshed_password = make_password(password)
        user = User.objects.create(password=harshed_password, username=uniqueidentifier, 
        first_name =profile.first_name,last_name= profile.last_name, email= profile.email_addres or 'none')
        user.refresh_from_db()
        user.is_active = True
        user.save()
        # form.user_id = user_id
        chars = '0123456789' 
        token = ''
        for num in range(0,len(chars)):
            token = token +chars[round((random()-0.5)*len(chars))]
        token = token[0:6]
        profile.last_token = make_password(token)
        profile.user = user
        profile.save()

        user.is_active = True
        user.save()
        login(request, user)
        allObject = inherit(request)
        # customer = apmodels.customer.objects.get(user=user)
        # customer = True
        template_name = 'customers/dashboard.html'
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'logged_in':True,
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
                redirecturl = redirect('admin_dashboard').url
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
    auth.logout(request)
    form = allauthforms.LoginForm()
    allObject = inherit(request, *args, **kwargs)
    allObject['form'] = form
    template_name = 'allauth/account/login.html'
    content = loader.render_to_string(template_name,allObject,request)
    output_data = {
                        'content':content,
                    }
    return redirect('customer_home')



@login_required
def account_activation_sent(request,*args, **kwargs):
    template_name = 'allauth/account/verification_sent.html'
    return render(request,template_name)



@login_required
def accept_privacy_terms(request, *args, **kwargs):
    allObject = inherit(request, *args, **kwargs)
    user = User.objects.get(pk=request.user.pk)
    customer = apmodels.Customer.objects.get(user=user)
    allObject['title']='DPG | Privacy, Terms and Conditions'
    if request.method == 'POST':
        customer.privacy_terms_accepted = True
        customer.save()

        return redirect('customer_dashboard')
    else:
        if request.GET.get('next'):
            allObject['next_page']=request.GET.get('next')
            allObject['redirect_url']=''.join(tuple(request.GET.get('next')))
        template_name = 'allauth/account/privacy_terms.html'
        return render(request,template_name,allObject)
        content = loader.render_to_string(template_name,allObject,request)
        output_data = {
                            'content':content,
                        }
        return JsonResponse(output_data)


@login_required
def createaccounts(request,*args, **kwargs):
    user = User.objects.get(email=request.user.email)
    try:
        customer = apmodels.Customer.objects.get(user=user)
        try:
            apmodels.SavingsAccount.objects.get(customer=customer)

        except ObjectDoesNotExist:
            apmodels.SavingsAccount.objects.create(customer=customer,number=str(round(random()*1234567890999))[0:10])
        try:
            apmodels.DebitAccount.objects.get(customer=customer)

        except ObjectDoesNotExist:
            apmodels.DebitAccount.objects.create(customer=customer,number=str(round(random()*1234567890999))[0:10])
        customer.accounts_created = True
        customer.save()
        output_data = {
                    'accounts_created':True,
                }
        return JsonResponse(output_data)  
    except ObjectDoesNotExist:
        customer = apmodels.Customer.objects.get(user=user)
        try:
            apmodels.Wallet.objects.get(userid=customer.userid)
            output_data = {
                        'wallet_created':True,
                    }
            return JsonResponse(output_data) 
        except ObjectDoesNotExist:
            apmodels.Wallet.objects.create(userid=customer.userid,number=str(round(random()*1234567890999))[0:10])
            output_data = {
                        'wallet_created':True,
                    }
            return JsonResponse(output_data)        


@login_required
def activate(request,*args, **kwargs):
    if request.method=='POST':
        user = User.objects.get(email=request.user.email)
        activation_code = request.POST.copy().get('activation_code')
        try:
                customer = apmodels.Customer.objects.get(user=user,)
        except ObjectDoesNotExist:
                customer = apmodels.Customer.objects.get(user=user,)
        passwordcheck = check_password(str(activation_code),str(customer.last_token))

        if passwordcheck:
            customer.email_confirmed = True
            customer.last_token=''
            customer.save()

            output_data = {
                'modal_message':'Account successfully activated',
                        'activated':True,
                        'next_url':request.POST.copy().get('next')
                        
                    }
            return JsonResponse(output_data)
        else:
            output_data = {
                        'invalid_code':True,
                    }
            return JsonResponse(output_data)






@login_required
def resendactivationcode(request,*args, **kwargs):
    chars = '0123456789'
    token = ''
    for num in range(0,len(chars)):
        token = token +chars[round((random()-0.5)*len(chars))]
    token = token[0:6] 
    user = request.user
    # user=User.objects.get(email=request.user.email)
    customer = apmodels.Customer.objects.get(user=user)
    customer.last_token=make_password(token)
    customer.save()
    subject = 'DPG - Activation Code'
    message = render_to_string('allauth/account/email_confirm.html', {
            'token':token,
            'user':user
        })
    email_from = settings.EMAIL_HOST_USER 
    recipient_list = [user.email, ] 
    try:
        send_mail( subject, message, email_from, recipient_list ) 
    except socket.gaierror:
        output_data = {
                'email_sent':True,
                'modal_notification':token,
                    }
        pass
    except smtplib.SMTPConnectError:
        output_data = {
                'email_sent':True,
                'modal_notification':token,
                    }
    output_data = {
                    'email_sent':True,
                    'modal_notification':token,
                        }
    # output_data = {
    #         'email_sent':True,
    #         'modal_notification':token,
    #             }

    
    return JsonResponse(output_data)
