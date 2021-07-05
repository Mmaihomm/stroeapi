from rest_framework import serializers
from .models import Category,Cart,Product,ProductImage,Invoice,Invoice_item,CHOICE_STATUS
from django.contrib.auth.models import User
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer

from rest_framework_simplejwt.tokens import RefreshToken
from django.utils.translation import gettext_lazy as _
from rest_framework.exceptions import AuthenticationFailed,ValidationError,NotFound
from django.contrib.auth.password_validation import validate_password

import requests
from versatileimagefield.serializers import VersatileImageFieldSerializer

class TokenObtainLifetimeSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            refresh = self.get_token(self.user)
            data['token_type'] = str(refresh.token_type)
            data['exprires_in'] = int(refresh.access_token.lifetime.total_seconds())
            return data
        except:
            raise AuthenticationFailed({'msg':'ชื่อผู้ใช้หรือรหัสผ่านไม่ถูกต้อง','code':'LOGIN_FAIL'})
        return super().validate(attrs)


class TokenRefreshLifetimeSerializer(TokenRefreshSerializer):
    
    def validate(self, attrs):
        try:
            data = super().validate(attrs)
            refresh = RefreshToken(attrs['refresh'])
            data['token_type'] = str(refresh.token_type)
            data['expires_in'] = int(refresh.access_token.lifetime.total_seconds())
            data['refresh_token'] = str(refresh)
            return data
        except:
            raise AuthenticationFailed({'msg':'Refetch Token ไม่ถูกต้อง','code':'REFETCH_TOKEN_FAIL'})
        return super().validate(attrs)

class UserSerializer(serializers.ModelSerializer):

    # username = serializers.CharField(max_length=20,error_message={"blank" : 'กรุณากรอกชื่อผู้ใช้งาน'})

    class Meta:
        model = User
        fields = ['username', 'password',  'is_superuser', 'first_name', 'last_name', 'email', 'is_active', 'is_staff' , 'date_joined']
        
    def validate_password(self, password):
        
        if len(password) < 8 :
            raise ValidationError('รหัสผ่านต้องมากกว่า 8 ตัว')
        
        return password 

    def create_user(self):
        user = User.objects.create_user(
            username= validated_data['username'],     
            password = validated_data['password']  ,
            first_name=validated_data['first_name'],  
            last_name=validated_data['last_name'])
        print(user)
        user.save()   
        return user

class RegisterSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['username', 'password', 'first_name', 'last_name']
        
    def validate_password(self, password):
        
        if len(password) < 8 :
            raise ValidationError('รหัสผ่านต้องมากกว่า 8 ตัว')
        
        return password 

    def create(self,validated_data):
        user = User.objects.create_user(
            username= validated_data['username'],     
            password = validated_data['password']  ,
            first_name=validated_data['first_name'],  
            last_name=validated_data['last_name'])
        user.save()   
        return user

        
class ProductImageSerializer(serializers.HyperlinkedModelSerializer):
    # product = serializers.PrimaryKeyRelatedField(many=True, queryset=Product.objects.all())
    image = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__100x100'),
            ('medium_square_crop', 'crop__400x400'),
            ('small_square_crop', 'crop__50x50')
        ]
    )
    class Meta:
        model = ProductImage
        fields = ('product','image')

class ProductSerializer(serializers.ModelSerializer):
    images = ProductImageSerializer(many=True, read_only=True)
    image = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__100x100'),
            ('medium_square_crop', 'crop__400x400'),
            ('small_square_crop', 'crop__50x50')
        ]
    )
    class Meta:
        model = Product
        fields = ('url','category','name', 'price' , 'detail', 'image', 'images','is_enable',)

class CategorySerializer(serializers.ModelSerializer):
    product = ProductSerializer(many=True, read_only=True)
    image = VersatileImageFieldSerializer(
        sizes=[
            ('full_size', 'url'),
            ('thumbnail', 'thumbnail__100x100'),
            ('medium_square_crop', 'crop__400x400'),
            ('small_square_crop', 'crop__50x50')
        ]
    )
    class Meta:
        model = Category
        fields = ('url','name','image','detail','is_enable','product')

class CartSerializer(serializers.ModelSerializer):
    product = serializers.CharField(max_length=10, error_messages={"blank": "กรุณากรอกรหัสสินค้า",'write_only':True})
    quantity = serializers.IntegerField(error_messages={"blank": "จำนวนสินค้านี้ต้องมากกว่า 0",'write_only':True})

    class Meta:
        model = Cart
        fields = ('product', 'user', 'quantity' , 'total')
        extra_kwargs = {'quantity':{'write_only':True}}

    def validate_product(self, product):
        try:
            is_enableds = Product.objects.get(pk = int(product))
        except:
            raise ValidationError('ไม่พบสินค้าชิ้นนี้')
            
        if not is_enableds.is_enable:
            raise ValidationError('สินค้านี้ถูกปิดการใช้งาน')
        return product

    def validate_quantity(self,quantity):
        if quantity < 1 :
            raise ValidationError('จำนวนสินค้านี้ต้องมากกว่า 0')
        return quantity 

    

class InvoiceSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Invoice
        fields = ('url','id','user' , 'created_datetime' , 'updated_datetime' , 'total' , 'status')

class Invoice_itemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Invoice_item
        fields = ('product' , 'invoice' , 'created_datetime' , 'quantity' , 'total')

class InvoiceDetailSerializer(serializers.ModelSerializer):
    # invoice_items = Invoice_itemSerializer(many=True,read_only=True)
    class Meta:
        model = Invoice
        fields = ('id','user' , 'created_datetime' , 'updated_datetime' , 'total' , 'status' )

