from ntpath import basename
from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, get_object_or_404
from django.views.static import serve
from .views import  *
from .api import *
from rest_framework import routers

router=routers.DefaultRouter()

router.register('top_categories',TopCategoriesView,basename='top_categories')

urlpatterns=[
      path('store/<str:id>/', StoreHome.as_view() , name='store_home'),
      path('', Home.as_view() , name='store_home'),
      path('store/products/<str:id>/',StoreProducts.as_view(),name='store_product'),   
      path('slideshows', SlideShowView.as_view(), name='customer_slideshows'),
      path('orders/<str:id>',MyOrderView.as_view(),name='orders'),
      path('download_order/<str:id>',OrderDownloadView.as_view(),name='order_download'),
      path('remove_order/<str:id>',RemoveOrderView.as_view(),name='remove_order'),
      path('error_500', Error500PageView.as_view(), name='customer_error_500'),
      path('error_400', Error400PageView.as_view(), name='customer_error_400'),
      path('carted_product/<str:id>', CartedProductView.as_view(), name='customer_carted_product'),
      path('new_products', NewProductView.as_view(), name='customer_new_products'),
      path('pay_on_delivery/<str:id>', PayOnDeliveryView.as_view(), name='customer_pay_on_delivery'),
      path('remove_from_cart/<str:id>', RemoveFromCartView.as_view(), name='customer_remove_carted_product'),
      
      
      path('home_group/<str:id>', HomeGroupProductsView.as_view(), name='customer_home_group_products'),
      path('flashsale/all/products/<str:id>', AllFlashSaleProductsView.as_view(), name='all_customer_flash_sales_products'),
      path('flashsale/', FlashSalePageView.as_view(), name='customer_flash_sales_page'),
      path('brand/<str:id>', BrandPageView.as_view(), name='customer_brand_page'),
      path('brand/products/<str:id>', BrandProductsView.as_view(), name='customer_brand_products'),


]+router.urls