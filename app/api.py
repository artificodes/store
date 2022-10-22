# from curses import flash
from ast import Pass
import random
import string
from winreg import REG_RESOURCE_LIST
import geoip2.database
import requests
import json
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from .models import *
from .serializer import *
from django.core.exceptions import (ObjectDoesNotExist,)
from django.core import exceptions
from app.views import(allproducts, cartedproduct, inherit,logrequest,customer_login_required,verifypayment,verifypaymentinine)
from paystackapi.paystack import Paystack
from paystackapi.transaction import Transaction
from paystackapi.verification import Verification
from seller import models as smodels
from store_admin import models as admodels
import os
from django.template import loader
from app.email_sender import sendmail
from django.core.mail import send_mail
from django.shortcuts import redirect
from app import models as apmodels
from .paginator import CustomPageNumberPagination
from app import serializer
from wkhtmltopdf.views import PDFTemplateView,PDFTemplateResponse
from django.template.loader import render_to_string
from rest_framework.viewsets import ModelViewSet
paystack_secret_key = "sk_test_e6c40e9e83237dbb32096831467c6e6193a970cb"
paystack = Paystack(secret_key=paystack_secret_key)

def getstore(request,id):
    try:
        store=smodels.Store.objects.get(id=id,is_approved=True).values()
    except Exception:
        store=[]
    return store

def getflashsale():
    try:
        flash_sale = apmodels.FlashSale.objects.filter(end_date_time__gte=datetime.datetime.now(),start_date_time__lte =datetime.datetime.now()).first()
        return flash_sale

    except Exception:
        pass





class StoreHome(APIView):

   def get(self,request,id,*args,**kwargs):
       allObject = inherit(request, *args, **kwargs)
       logrequest(request,'')
       store=getstore(request,id)
    #    Serializer=StoreSerializer(store, many=True).data
       allObject['currentstore']=store
       
       
       return Response(allObject)


class Home(APIView):
    def get(self,request,*args,**kwargs):
       allObject = inherit(request, *args, **kwargs)
       logrequest(request,'')
       flash_sale=getflashsale()
       serializer=FlashSaleSerializer(flash_sale,many=True).data
       allObject['serializer']=serializer

       return Response(allObject)




class StoreProducts(APIView,CustomPageNumberPagination):

    pagination_class=CustomPageNumberPagination
    
    def get_object(self,id):
        try:
            store=smodels.Store.objects.get(id=id)
            return store
        except ObjectDoesNotExist:
            pass
        
    
    def get(self,request,id,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        logrequest(request,'')
        store=self.get_object(id)
        serializer=StoreSerializer(store,many=False).data
        allObject["serializer"]=serializer
        return Response(allObject)


class SlideShowView(APIView):
    queryset=list(apmodels.SlideShow.objects.all())
    def get(self,request,*args, **kwargs):
        allObject = inherit(request, *args, **kwargs)
        slideshow=self.queryset
        serializer=SlideShowSerializer(request.data,many=True).data
        allObject['serializer']=serializer
        return Response(allObject)


class TopCategoriesView(ModelViewSet):
    queryset=apmodels.Category.objects.filter(is_top=True)
    
    def list(self,request,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        allObject['serializer']=CategorySerializer(self.queryset,many=True).data
        return Response(allObject)

class MyOrderView(APIView):
    def get_object(self,id,allObject):
        if self.request.user.is_authenticated:
            try:
            
                customer=allObject['customer']
            
                order=apmodels.Order.objects.get(customer = customer,orderid=id)
                return order
            except:
                pass
            
        else:
            try:
                order=apmodels.Order.objects.get(session=self.request.session.session_key,orderid=id)
                return order
            except:
                pass
        
       

    def get(self,request,id,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        serializer=self.get_object(id,allObject)
        allObject['serializer']=OrderSerializer(serializer).data
        return Response(allObject)
        
        


class OrderDownloadView(APIView):

    def get_object(self,id,allObject):
        if self.request.user.is_authenticated:
            customer=allObject['customer']
            try:
                order = apmodels.Order.objects.get(customer = customer,orderid=id)
                return order
            except ObjectDoesNotExist:
                pass
        else:
            try:
             order = apmodels.Order.objects.get(session = self.request.session.session_key,orderid=id)
             return order
            except ObjectDoesNotExist:
                pass 
        

    def get(self,request,id,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        order_qs=self.get_object(id,allObject)
        order=OrderSerializer(order_qs,many=False).data  
        allObject['serializer']=order
        filename=order_qs.orderid
        for product in order_qs.products.all():
            encoded_string = ''
            try:
                with open(product.product.image.path, 'rb') as img_f:
                    encoded_string = base64.b64encode(img_f.read()).decode()
                image= 'data:image/%s;base64,%s' % ('png', encoded_string)
                product.product.base64 = image
                product.product.save()    
            except ValueError:
                pass
        order_qs.refresh_from_db()
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
        return Response(response)



class RemoveOrderView(APIView):
    serializer_class=OrderSerializer

    def get_object(self,id,allObject):
        customer = False
        if self.request.user.is_authenticated:
            customer = allObject['customer']
            try:
                order = apmodels.Order.objects.get(customer = customer,orderid=id)
            except ObjectDoesNotExist:
                pass
            
        else:
            try:
                order = apmodels.Order.objects.get(session = self.request.session.session_key,orderid=id)

            except ObjectDoesNotExist:
                pass
    
    def get_queryset(self,allObject):
        if self.request.user.is_authenticated:
            customer = allObject['customer']
            try:
                orders = apmodels.Order.objects.filter(customer = customer,deleted=False)
            except ObjectDoesNotExist:
                pass
            
        else:
            try:
                orders = apmodels.Order.objects.filter(session = self.request.session.session_key,deleted=False)

            except ObjectDoesNotExist:
                pass

    def get(self,request,id,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        order=self.get_object(id,allObject)
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

        orders=self.get_queryset(allObject)
        allObject['serializer']=OrderSerializer(orders, many=True).data
        return Response(allObject)
        

class Error500PageView(APIView):

    def get_queryset(self,allObject):

        if self.request.user.is_authenticated:
            user=self.request.user.pk
            
            if user.is_superuser:
                pass
            else:
                try:
                    current_user = apmodels.Customer.objects.get(user=user.pk).values()
                    # allObject['user'] = user
                    allObject['customer'] = current_user
                    customer = allObject['customer']      
                        
                except ObjectDoesNotExist:
                    pass        
                customer = allObject['customer']
                try:
                    orders = apmodels.Order.objects.filter(customer = customer,deleted=False).values()
                    allObject['orders'] = orders
                    # return orders

                except ObjectDoesNotExist:
                    pass
                try:
                    saved = apmodels.SavedProduct.objects.get(customer = customer,).values()
                    allObject['saved'] = len(saved.products.all()) or 0
                except ObjectDoesNotExist:
                    pass

        else:
            try:
                orders = apmodels.Order.objects.filter(session = self.request.session.session_key,).values()
                allObject['orders'] = orders

            except ObjectDoesNotExist:
                pass
            try:
                saved = apmodels.SavedProduct.objects.get(session = self.request.session.session_key,).values()
                allObject['saved'] = len(saved.products.all()) or 0

            except ObjectDoesNotExist:
                pass
        
    
    def get(self,request,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        allObject['serializer']=self.get_queryset(allObject)
        return Response(allObject)
    

class Error400PageView(APIView):
    def get_queryset(self,allObject):
        try:
            store = list(admodels.General.objects.all())[0]
        except IndexError:
            store =[] 
        if self.request.user.is_authenticated:
            user=self.request.user
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
                    orders = apmodels.Order.objects.filter(customer = customer,deleted=False).values()
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
                orders = apmodels.Order.objects.filter(session = self.request.session.session_key,).values()
                allObject['orders'] = orders

            except ObjectDoesNotExist:
                pass
            try:
                saved = apmodels.SavedProduct.objects.get(session = self.request.session.session_key,).values().values()
                allObject['saved'] = len(saved.products.all()) or 0

            except ObjectDoesNotExist:
                pass
    
    def get(self,request,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        allObject['serializer']=self.get_queryset(allObject)
        return Response(allObject)



class CartedProductView(APIView):
    def get_object(self,id):
        try:
            cartedproduct = apmodels.CartedProduct.objects.get(cartedproductid=id)
            return cartedproduct
        except ObjectDoesNotExist:
            pass
    

    def get(self,request,id,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        cartedproduct=self.get_object(id)
        flashsales=FlashSaleSerializer(getflashsale(),many=True).data
        for flashsale in flashsales:
            for flashsaleproduct in flashsale.products.all():
                if cartedproduct.product == flashsaleproduct.product:
                    return Response(flashsaleproduct)


        allObject['product'] = CartedProductSerializer(cartedproduct,many=False).data
        return Response(allObject)


#Paginated view
class NewProductView(APIView):
    pagination_class=CustomPageNumberPagination

    def get_queryset(self,request):
        allproducts = list(apmodels.Product.objects.all())
        allproducts.sort(key=lambda x:x.date_time_added,reverse=True)
        new_products = allproducts[:5]
        return new_products

    def get(self,request,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)

        serializer=ProductSerializer(self.get_queryset(request),many=True)
        allObject['serializer']=serializer.data
        allObject['paginatedproducts'] = str(request.path)
        allObject['section'] = 'new-products'

        return Response(allObject)



class PayOnDeliveryView(APIView):
    def get_object(self,id):
        try:
            order = apmodels.Order.objects.get(orderid=id)
            return order
        except ObjectDoesNotExist:
            pass
        
    
    def get(self,request,id,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        customer = allObject['customer']
        order=self.get_object(id)
        order.payment_method='pd'
        order.save()
        order.refresh_from_db()
        serializer=OrderSerializer(order,many=False).data
        message = render_to_string('app/templates/order_placed_email.html', {
            'order':serializer,
            'customer':customer,
            'title':'ORDER PLACED',
            'socials':admodels.SocialLink.objects.all(),
            'store':allObject['store']
        })
        for product in order.products.all():
            product.product.purchase_count +=product.quantity
            product.ordered= True
            product.save()
            store = smodels.Store.objects.filter(products=product.product)[0]
            store.orders.add(product)
            product.product.save()
        subject = 'New Order Placed - '+serializer.orderid
        recipient_list = [allObject['store'].email, ]
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
        return Response(output_data)


class RemoveFromCartView(APIView):

    def get(self,request,id,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        customer = False
        if request.user.is_authenticated:
            customer = allObject['customer']
            try:
                cart = apmodels.Cart.objects.get(customer = customer).values()
                
            except ObjectDoesNotExist:
                pass
            try:
                cartedproduct = apmodels.CartedProduct.objects.get(cartedproductid=id,).values()
               
            except ObjectDoesNotExist:
                pass
            
        else:
            try:
                cart = apmodels.Cart.objects.get(session = request.session.session_key).values()
               
            except ObjectDoesNotExist:
                pass
            try:
                cartedproduct = apmodels.CartedProduct.objects.get(cartedproductid=id,).values()
                
            except ObjectDoesNotExist:
                pass
       
        try:
            cartedproduct.delete()        
            cart.save()
            cart.refresh_from_db()
            return Response({"message":"cart successfully deleted"})
        except:
             return Response({"message":"couldn't delete cart"})



class HomeGroupProductsView(APIView):
    pagination_class=CustomPageNumberPagination
    def get_object(self,id):
        try:
            home_group = apmodels.HomePageGroup.objects.get(pk=id)
            return home_group
        except:
           pass
        
    
    def get(self,request,id,*args,**kwargs):
       allObject = inherit(request, *args, **kwargs)
       home_group=HomePageGroupSerializer(self.get_object(id),many=False).data
       allproducts=home_group.products.all()[:10]
       allObject['serializer']=allproducts
       allObject['section']=home_group.slug
       allObject['paginatedproducts'] = str(request.path)

       return Response(allObject)
       

class AllFlashSaleProductsView(APIView):
    pagination_class=CustomPageNumberPagination
    def get_object(self,id):
        try:
            allproducts = apmodels.FlashSale.objects.get(pk=id).products.all()
            return allproducts
        except:
            pass
        


    def get(self,request,id,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        allproducts=self.get_object(id)
        products=[]
        serializer=FlashSaleSerializer(allproducts,many=False).data
        for product in serializer:
            products.append(product.product)
        allObject['products'] = products
        allObject['paginatedproducts'] = str(request.path)

        return Response(allObject)



class FlashSalePageView(APIView):
    def get(self,request,*args,**kwargs):
        logrequest(request,'')
        allObject = inherit(request, *args, **kwargs)
        flashsale = apmodels.FlashSale.objects.all().first()

        allObject['title']='Flashsale | Intelbyt'
        allObject['serializer']=FlashSaleSerializer(flashsale,many=True).data

        return Response(allObject)



class BrandPageView(APIView):

    
    def get_object(self,id):
        try:
            brand = apmodels.Brand.objects.get(id=id)
            return brand
        except:
            pass

    def get(self,request,id,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        brand_obj=self.get_object(id)
        brand=BrandSerializer(brand_obj,many=False).data
        allObject['serializer']=brand
        allObject['title']=brand_obj.name + ' '+ allObject['store'].store_name

        return Response(allObject)





class BrandProductsView(APIView):
    def get_object(self,id):
        try:
            brand = apmodels.Brand.objects.get(id=id)
            products=list(brand.products.all())
            products.sort(key=lambda x:x.date_time_added,reverse=True)
            return products
        except:
            pass

    
    def get(self,request,id,*args,**kwargs):
        allObject = inherit(request, *args, **kwargs)
        products=self.get_object(id)

        allObject['serializer']=products
        return Response(allObject)
        