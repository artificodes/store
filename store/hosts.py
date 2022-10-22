from django_hosts import patterns, host
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from django.conf.urls.static import static

host_patterns = patterns('',
    host(r'www', settings.ROOT_URLCONF, name='www'),
    host(r'admin', 'admin.urls', name='admin'),
    host(r'user', 'user.urls', name='user'),

)  
