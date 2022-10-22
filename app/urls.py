from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib import admin
from django.conf.urls import url, include
from django.conf import settings
from django.conf.urls.static import static
from django.shortcuts import render, get_object_or_404
from django.views.static import serve
from app import views as apviews




urlpatterns = [    
    # path('', apviews.home, name='store_home'),
    path('store/<str:slug>/', apviews.storehome, name='store_home'),    
    path('', apviews.home, name='customer_home'),
    path('store/products/<str:slug>', apviews.storeproducts, name='customer_store_products'),

    path('slideshows', apviews.slideshows, name='customer_slideshows'),
    path('top_categories', apviews.topcategories, name='customer_top_categories'),
    path('order/<str:orderid>', apviews.myorder, name='customer_my_order'),
    path('download_order/<str:orderid>', apviews.downloadorder, name='customer_download_order'),
    path('remove_order/<str:id>', apviews.remove_order, name='customer_remove_order'),
    # path('checkout', apviews.checkout, name='customer_checkout'),
    path('error_500', apviews.error500page, name='customer_error_500'),
    path('error_404', apviews.error404page, name='customer_error_404'),
    path('carted_product/<str:id>', apviews.cartedproduct, name='customer_carted_product'),
    path('new_products', apviews.newproducts, name='customer_new_products'),
    path('pay_on_delivery/<str:orderid>', apviews.payondelivery, name='customer_pay_on_delivery'),
    path('remove_from_cart/<str:id>', apviews.remove_from_cart, name='customer_remove_carted_product'),
    path('home_group/<str:id>', apviews.homegroupproducts, name='customer_home_group_products'),
    path('flashsale/all/products/<str:id>', apviews.allflashsaleproducts, name='all_customer_flash_sales_products'),
    path('flash_sales_products/<str:id>', apviews.flashsaleproducts, name='customer_flash_sales_products'),
    path('flashsale/', apviews.flashsalespage, name='customer_flash_sales_page'),
    path('brand/<str:slug>', apviews.brandpage, name='customer_brand_page'),
    path('brand/products/<str:slug>', apviews.brandproducts, name='customer_brand_products'),
    path('slide/<str:slug>', apviews.slideshowpage, name='customer_slideshow_page'),
    path('slideshow/products/<str:slug>', apviews.slideshowproducts, name='customer_slideshow_products'),
    path('flash_sales_product/<str:id>', apviews.flashsaleproduct, name='customer_flash_sales_product'),
    path('product/<str:id>', apviews.product, name='customer_product'),
    path('product_details/<str:productid>', apviews.product_details, name='customer_product_details'),
    path('add_to_cart/<str:productid>', apviews.add_to_cart, name='customer_add_to_cart'),
    path('add_variation_to_cart/', apviews.add_variation_to_cart, name='customer_add_variation_to_cart'),
    path('similiar_products/<str:productid>', apviews.similarproducts, name='customer_similar_products'),
    path('add_to_saved/<str:productid>', apviews.add_to_saved, name='customer_add_to_saved'),
    path('remove_from_saved/<str:productid>', apviews.remove_from_saved, name='customer_remove_from_saved'),
    path('category/<str:name>', apviews.categorys, name='customer_our_offers'),
    path('offer_products/<str:name>', apviews.categoryproducts, name='customer_offer_products'),
    path('category/<str:name>', apviews.categorys, name='customer_our_categorys'),
    path('group/<str:slug>', apviews.homegroup, name='customer_home_group'),
    path('group/products/<str:slug>', apviews.allhomegroupproducts, name='all_customer_home_group_products'),
    path('group/all/', apviews.allhomegroupsection, name='all_customer_home_group_sections'),
    path('newsletter/subscribe/', apviews.newlettersubscription, name='customer_news_letter_subscription'),
    path('brand/<str:name>', apviews.categorys, name='customer_brands'),
    path('category_products/<str:name>', apviews.categoryproducts, name='customer_category_products'),
    path('update_cart/', apviews.update_cart, name='customer_update_cart'),
    path('cart_count/', apviews.cart_count, name='customer_cart_count'),
    path('products/all', apviews.allproducts, name='customer_all_products'),
    path('products/page/all', apviews.allproductspage, name='customer_all_products_page'),
    path('products/paginated', apviews.paginatedproducts, name='customer_paginated_products'),
    path('products_you_may_like/', apviews.products_you_may_like, name='customer_products_you_may_like'),
    path('saved_items/', apviews.saveditemspage, name='customer_saved_items_page'),
    path('saved_items/products', apviews.savedproducts, name='customer_saved_items_products'),
    path('search/', apviews.search_products, name='customer_search_products'),
    path('place_order/', apviews.place_order, name='customer_place_order'),
    path('my_orders/', apviews.myorders, name='customer_my_orders'),

    path('cart/', apviews.cartpage, name='customer_cart_page'),
    path('customer/cart/', apviews.cart, name='customer_cart'),
    path('update_contact_details/', apviews.updatecontactdetails, name='customer_update_contact_details'),
    path('order_paid', apviews.orderpaid, name='customer_order_paid'),
    path('verify_payment', apviews.verifypayment, name='customer_verify_payment'),
     path("customer/signup/",apviews.customersignup,name='customer_signup'),
      url("customer/auth/", apviews.loginuser, name='customer_auth'),
    # #   url("customer/new/accounts/signup/", apviews.signup, name='customer_signup'),
    #   url("customer/privacy_terms/accept/", gviews.accept_privacy_terms, name='customer_accept_privacy_terms'),

      # path("accounts/signup/",gviews.signup,name='account_signup'),
      url("customer/login/", apviews.customerlookup, name='customer_login'),

      # url("accounts/login/", gviews.loginuser, name='account_login'),
      # url("", gviews.loginuser, name='login'),
      url("customer/logout", apviews.logoutuser, name='customer_logout'),
    # url(r'^account_activation_sent/$', gviews.account_activation_sent,
    #     name='customer_account_activation_sent'),
    # # url(r'^accounts/', include('allauth.urls')),
    # url('activate-account', gviews.activate, name='customer_activate_account'),
    # url('createwallet', gviews.createaccounts, name='customer_create_accounts'),
    # url('resendactivationcode', gviews.resendactivationcode,
    #     name='customer_resend_activation_code'),
    # url('unsuspend', gviews.unsuspend, name='customer_unsuspend'),
    path('select_account_type/', apviews.select_account_type, name='customer_select_account_type'),
    path('confirmemail', apviews.confirmemail, name='customer_confirm_email'),
    path('confirmemailpage/', apviews.confirmemailpage, name='customer_confirm_email_page'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
