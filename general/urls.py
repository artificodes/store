from django.contrib import admin
from django.urls import path
from django.urls import path, include, re_path
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, get_object_or_404
from django.views.static import serve
from general import views as gviews


urlpatterns = [
  
    # path('home',gviews.home,name='home'),
      # path("customer/accounts/signup/",gviews.customersignup,name='customer_account_signup'),
      # url("customer/accounts/auth/", gviews.loginuser, name='customer_account_auth'),
      # url("customer/new/accounts/signup/", gviews.signup, name='customer_new_account_signup'),
      # url("customer/privacy_terms/accept/", gviews.accept_privacy_terms, name='customer_accept_privacy_terms'),

      # # path("accounts/signup/",gviews.signup,name='account_signup'),
      # url("customer/accounts/login/", gviews.customerlookup, name='customer_account_login'),

      # # url("accounts/login/", gviews.loginuser, name='account_login'),
      # # url("", gviews.loginuser, name='login'),
      # url("customer/logout", gviews.logoutuser, name='customer_account_logout'),

      url(r'^account_activation_sent/$', gviews.account_activation_sent, name='account_activation_sent'),
  url(r'^accounts/', include('allauth.urls')),
    url('activate-account', gviews.activate, name='activate_account'),
    url('createwallet', gviews.createaccounts, name='create_accounts'),
    url('resendactivationcode', gviews.resendactivationcode, name='resend_activation_code'),
    url('unsuspend', gviews.unsuspend, name='unsuspend'),

]
urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
