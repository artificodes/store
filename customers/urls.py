from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, get_object_or_404
from django.views.static import serve
from customers import views as cviews
from general import views as gviews



urlpatterns = [    
    
    path('', cviews.home, name='customer_home'),
    path('home', cviews.home, name='customer_home'),
    path('slideshows', cviews.slideshows, name='customer_slideshows'),
    path('order/<str:orderid>', cviews.myorder, name='customer_my_order'),
    path('download_order/<str:orderid>', cviews.downloadorder, name='customer_download_order'),
    path('remove_order/<str:id>', cviews.remove_order, name='customer_remove_order'),
    path('checkout', cviews.checkout, name='customer_checkout'),
    path('error_500', cviews.error500page, name='customer_error_500'),
    path('error_404', cviews.error404page, name='customer_error_404'),
    path('carted_product/<str:id>', cviews.cartedproduct, name='customer_carted_product'),
    path('new_products', cviews.newproducts, name='customer_new_products'),
    path('pay_on_delivery/<str:orderid>', cviews.payondelivery, name='customer_pay_on_delivery'),
    path('remove_from_cart/<str:id>', cviews.remove_from_cart, name='customer_remove_carted_product'),
    path('home_group/<str:id>', cviews.homegroupproducts, name='customer_home_group_products'),
    path('flashsale/all/products/<str:id>', cviews.allflashsaleproducts, name='all_customer_flash_sales_products'),
    path('flash_sales_products/<str:id>', cviews.flashsaleproducts, name='customer_flash_sales_products'),
    path('flashsale/<str:id>', cviews.flashsalespage, name='customer_flash_sales_page'),
    path('brand/<str:slug>', cviews.brandpage, name='customer_brand_page'),
    path('brand/products/<str:slug>', cviews.brandproducts, name='customer_brand_products'),
    path('slideshow/<str:slug>', cviews.slideshowpage, name='customer_slideshow_page'),
    path('slideshow/products/<str:slug>', cviews.slideshowproducts, name='customer_slideshow_products'),
    path('flash_sales_product/<str:id>', cviews.flashsaleproduct, name='customer_flash_sales_product'),
    path('product/<str:id>', cviews.product, name='customer_product'),
    path('product_details/<str:productid>', cviews.product_details, name='customer_product_details'),
    path('add_to_cart/<str:productid>', cviews.add_to_cart, name='customer_add_to_cart'),
    path('add_variation_to_cart/', cviews.add_variation_to_cart, name='customer_add_variation_to_cart'),
    path('similiar_products/<str:productid>', cviews.similarproducts, name='customer_similar_products'),
    path('add_to_saved/<str:productid>', cviews.add_to_saved, name='customer_add_to_saved'),
    path('remove_from_saved/<str:productid>', cviews.remove_from_saved, name='customer_remove_from_saved'),
    path('category/<str:name>', cviews.categorys, name='customer_our_offers'),
    path('offer_products/<str:name>', cviews.categoryproducts, name='customer_offer_products'),
    path('category/<str:name>', cviews.categorys, name='customer_our_categorys'),
    path('group/<str:slug>', cviews.homegroup, name='customer_home_group'),
    path('group/products/<str:slug>', cviews.allhomegroupproducts, name='all_customer_home_group_products'),
    path('group/all/', cviews.allhomegroupsection, name='all_customer_home_group_sections'),
    path('newsletter/subscribe/', cviews.newlettersubscription, name='customer_news_letter_subscription'),
    path('brand/<str:name>', cviews.categorys, name='customer_brands'),
    path('category_products/<str:name>', cviews.categoryproducts, name='customer_category_products'),
    path('update_cart/', cviews.update_cart, name='customer_update_cart'),
    path('cart_count/', cviews.cart_count, name='customer_cart_count'),
    path('products/all', cviews.allproducts, name='customer_all_products'),
    path('products/page/all', cviews.allproductspage, name='customer_all_products_page'),
    path('products/paginated', cviews.paginatedproducts, name='customer_paginated_products'),
    path('products_you_may_like/', cviews.products_you_may_like, name='customer_products_you_may_like'),
    path('saved_items/', cviews.saveditemspage, name='customer_saved_items_page'),
    path('saved_items/products', cviews.savedproducts, name='customer_saved_items_products'),
    path('search/', cviews.search_products, name='customer_search_products'),
    path('place_order/', cviews.place_order, name='customer_place_order'),
    path('my_orders/', cviews.myorders, name='customer_my_orders'),

    path('cart/', cviews.cart, name='customer_cart'),
    path('update_contact_details/', cviews.updatecontactdetails, name='customer_update_contact_details'),
    path('order_paid', cviews.orderpaid, name='customer_order_paid'),
    path('verify_payment', cviews.verifypayment, name='customer_verify_payment'),
    path("accounts/signup/", gviews.signup, name='customer_account_signup'),
    url("accounts/login/", gviews.loginuser, name='customer_account_login'),
    url("accounts/logout/", gviews.logoutuser, name='customer_account_logout'),

    url(r'^account_activation_sent/$', gviews.account_activation_sent,
        name='customer_account_activation_sent'),
    url(r'^accounts/', include('allauth.urls')),
    url('activate-account', gviews.activate, name='customer_activate_account'),
    url('createwallet', gviews.createaccounts, name='customer_create_accounts'),
    url('resendactivationcode', gviews.resendactivationcode,
        name='customer_resend_activation_code'),
    url('unsuspend', gviews.unsuspend, name='customer_unsuspend'),
    path('select_account_type/', cviews.select_account_type, name='customer_select_account_type'),
    path('confirmemail', cviews.confirmemail, name='customer_confirm_email'),
    path('confirmemailpage/', cviews.confirmemailpage, name='customer_confirm_email_page'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
