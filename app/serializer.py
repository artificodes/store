from unicodedata import category
from rest_framework import serializers
from .models import *
from seller.models import Store

class VistorLogSerializer(serializers.ModelSerializer):
    class Meta:
        model=VisitorsLog
        fields='__all__'



class CustomerSerializer(serializers.ModelSerializer):
    class Meta:
        model=Customer
        fields='__all__'



class MeasurementUnitSerializer(serializers.ModelSerializer):
    class Meta:
        model=MeasurementUnit
        fields='__all__'




class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model=Tag
        fields='__all__'




class ProductVariationSerializer(serializers.ModelSerializer):
    class Meta:
        model=VisitorsLog
        fields='__all__'




class ProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=Product
        fields='__all__'




class HomePageGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model=HomePageGroup
        fields='__all__'


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model=Brand
        fields='__all__'




class BestDealSerializer(serializers.ModelSerializer):
    class Meta:
        model=BestDeal
        fields='__all__'



class CartedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=CartedProduct
        fields='__all__'




class DeliveryLocationSerializer(serializers.ModelSerializer):
    class Meta:
        model=DeliveryLocation
        fields='__all__'




class SavedProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=SavedProduct
        fields='__all__'

        



class CartSerializer(serializers.ModelSerializer):
    class Meta:
        model=SavedProduct
        fields='__all__'





class OrderSerializer(serializers.ModelSerializer):
    class Meta:
        model=Order
        fields='__all__'





class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model=ProductImage
        fields='__all__'





class SlideShowSerializer(serializers.ModelSerializer):
    class Meta:
        model=SlideShow
        fields='__all__'



class FlashSaleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model=FlashSaleProduct
        fields='__all__'




class SlideShowSerializer(serializers.ModelSerializer):
    class Meta:
        model=SlideShow
        fields='__all__'



class FlashSaleSerializer(serializers.ModelSerializer):
    class Meta:
        model=SlideShow
        fields='__all__'


class NewsLetterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model=NewsLetterSubscription
        fields='__all__'



class StoreSerializer(serializers.ModelSerializer):
    class Meta:
        model=Store
        fields='__all__'
    

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model=Category
        fields='__all__'