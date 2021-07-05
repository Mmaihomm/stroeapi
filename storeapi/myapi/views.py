from django.shortcuts import render
from rest_framework import generics, permissions, serializers
from django.contrib.auth.models import User
from django.contrib import admin
admin.autodiscover()
from .serializers import *
from .models import Category,Cart,Product,ProductImage,Invoice,Invoice_item
from rest_framework_simplejwt.views import TokenObtainPairView,TokenRefreshView
from django.http import HttpResponse, JsonResponse
# Create your views here.
import json


from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework.reverse import reverse
from rest_framework import status
from rest_framework.exceptions import NotFound,NotAuthenticated
from rest_framework import pagination
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend

from rest_framework_simplejwt.views import TokenViewBase
from .serializers import TokenObtainLifetimeSerializer, TokenRefreshLifetimeSerializer

from rest_framework_simplejwt.tokens import RefreshToken


@api_view(['GET'])
def api_root(request, format=None):
    return Response({
        'token_obtain_pair': reverse('token_obtain_pair', request=request, format=format),
        'refreshtoken': reverse('token_refresh', request=request, format=format),
        'register': reverse('register', request=request, format=format),
        'category': reverse('category-list', request=request, format=format),
        'product': reverse('product-list', request=request, format=format),
        'cart': reverse('cart-list', request=request, format=format),
        'invoice': reverse('invoice', request=request, format=format),
    })



class CustomPagination(pagination.PageNumberPagination):
    page_size = 5
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'   

class TokenObtainPairView(TokenViewBase):
    """
        Return JWT tokens (access and refresh) for specific user based on username and password.
    """
    serializer_class = TokenObtainLifetimeSerializer
    

class TokenRefreshView(TokenViewBase):
    """
        Renew tokens (access and refresh) with new expire time based on specific user's access token.
    """
    serializer_class = TokenRefreshLifetimeSerializer

class Register(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = RegisterSerializer
    def post(self, request, *args,  **kwargs):
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            # serializer.save()
            user = serializer.save()
            refresh = RefreshToken.for_user(user)
            return Response({ 
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'token_type' : str(refresh.token_type),
                'exprires_in' : int(refresh.access_token.lifetime.total_seconds())
            })
        else:
            return Response({
                 "msg" : "ลงทะเบียนไม่สำเร็จ",
                 "code": "REGISTER_FAIL",
                 "errors":serializer.errors,
            },status=status.HTTP_400_BAD_REQUEST)
        # Products.objects.filter(category__in=(1,2,3))
        
        #auto token
        # token, created = Token.objects.get_or_create(user=serializer.instance)

class ResponseInfo(object):
    def __init__(self, user=None, **args):
        self.response = {
            "msg": args.get('msg', 'ดึงข้อมูลสำเร็จ'),
            "data": args.get('data', []),
        }

class GetCategoryList(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['is_enable']
    def __init__(self, **kwargs):
        self.response_format = ResponseInfo().response
        super(GetCategoryList, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(GetCategoryList, self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = True
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)


class GetCategoryDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        if serializer.data:
            custom_data = {
                    "status": "ดึงข้อมูลสำเร็จ",
                    "data": serializer.data
            }
            return Response(custom_data)
        
    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj =  queryset.get(pk=self.kwargs['pk'])
            
        except:
            raise NotFound()
        return obj
        
        
    
class ResponseInfoProduct(object):
    def __init__(self, user=None, **args):
        self.response = {
            "msg": args.get('msg', 'ดึงข้อมูลสำเร็จ'),
            "data": args.get('data', []),
        }

class GetProductList(generics.ListAPIView):
    # permission_classes = [permissions.IsAuthenticated]
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['is_enable']

    def query_set(self):
        queryset = Product.objects.all()
        sort_by = self.request.query_params.get('sort','desc')
        category_in = self.request.query_params.get('category__in',None)
        category_not_in = self.request.query_params.get('category_not_in',None)
        list_category_in = []
        list_category_not_in = []

        #category in
        if category_in:
            for cat_in in category_in.split(","):
                list_category_in.append(int(cat_in))

        #category not in
        if category_not_in:
            for cat_in in category_not_in.split(","):
                list_category_not_in.append(int(cat_in))

        #sort
        if sort_by == 'desc':
            queryset = queryset.order_by('-price')
        else:
            queryset = queryset.order_by('price')
        

        if category_in:
            queryset = queryset.filter(category__in = list_category_in)

        if category_not_in:
            queryset = queryset.exclude(category__in = list_category_not_in)

        return queryset
        
    

    def __init__(self, **kwargs):
        self.response_format = ResponseInfoProduct().response
        super(GetProductList, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(GetProductList, self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = True
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)


    


class GetProductDetail(generics.RetrieveUpdateDestroyAPIView):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        if serializer.data:
            custom_data = {
                    "status": "ดึงข้อมูลสำเร็จ",
                    "data": serializer.data
            }
            return Response(custom_data)
        else:
            raise NotFound()

    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj =  queryset.get(pk=self.kwargs['pk'])
            
        except:
            raise NotFound()
        return obj


class AddtoCart(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer
    pagination_class = CustomPagination
    filter_backends = [DjangoFilterBackend,filters.SearchFilter,filters.OrderingFilter]
    filterset_fields = ['product']
    ordering_fields = ['quantity','total']

    def __init__(self, **kwargs):
        self.response_format = ResponseInfoProduct().response
        super(AddtoCart, self).__init__(**kwargs)
        
    def post(self, request, *args, **kwargs):
        
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            
            user_id = self.request.user
            user = User.objects.get(username=user_id)

            product_id = serializer.data['product']
            products = Product.objects.get(pk=int(product_id))

            quantities = int(serializer.data['quantity'])
            item = Cart.objects.filter(user=user,product=products.id).first()
            
            if item:

                item.quantity += quantities

                mul = quantities*products.price
                item.total += mul
            
                item.save()
            else:

                item = Cart.objects.create(product=products,user=user,quantity=quantities,total=quantities*products.price)
                item.save()
                # item = Cart.objects.filter(user=user)
            response_data = super(AddtoCart, self).list(request, *args, **kwargs)
            self.response_format["data"] = response_data.data
            self.response_format["status"] = True
            if not response_data.data:
                self.response_format["message"] = "List empty"
            return Response(self.response_format)
        else:

            return Response({
                "code" : "ADD TO CART FAIL",
                "msg" : "บันทึกไม่สำเร็จ",
                "error" : [serializer.errors]
            },status=status.HTTP_400_BAD_REQUEST)
        
        
        
            

class EditCartQuanlity(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def patch(self, request, pk):
        
        cartlist = Cart.objects.get(id=pk)
        data = request.data
        
        cartlist.total = int(data['quantity'])*(cartlist.product.price)
        cartlist.quantity = int(data['quantity'])
        cartlist.save()
        carttotal = CartSerializer(cartlist).data
        if cartlist.quantity == 0:
            cartlist.delete()
            return Response({
                "msg" : "ลบสำเร็จ"
            },status=200)
        return Response({
            "msg" : "บันทึกสำเร็จ",
            "data" : [carttotal]
        },status=200)
        
    def destroy(self, request, *args, **kwargs):
        current_user = self.request.user
        try:
            instance = self.get_object()
            cart_user = Cart.objects.get(pk=kwargs['pk']).user
        except:
            raise NotFound()
        #user forbidden
        if cart_user != current_user:
            return Response({
                "code" : "HTTP_403_FORBIDDEN",
                "msg" : "ไม่มีสิทธิ์เข้าใช้งาน"
            },status=status.HTTP_403_FORBIDDEN)


        self.perform_destroy(instance)
        return Response({
            "msg" : "ลบสำเร็จ"
        },status=status.HTTP_200_OK)     
        

class Checkout(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Cart.objects.all()
    serializer_class = CartSerializer

    def post(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        data ={}
        carts = Cart.objects.filter(user=self.request.user) 
        sum_total=0
        if len(carts)!=0:
            for i in carts:
                if not i.product.is_enable:
                    return Response({
                "code": "CHECKOUT_FAIL",
                "msg": "มีสินค้าบางรายการไม่สามารถสั่งซื้อได้",
                },status=status.HTTP_400_BAD_REQUEST)
                else:
                    sum_total += i.total
            
            invoices = Invoice.objects.create(user=self.request.user,total=sum_total)
        
            if invoices:
                invoices.save()
                for item in carts:
                    invoice_items = Invoice_item.objects.create(product=item.product,invoice=invoices,quantity=item.quantity,total=item.total)
                    if invoice_items:
                        invoice_items.save()
                        item.delete()
            else:
                return Response({
                "msg":"ไม่มีใบสั่งซื้อสินค้า",
                "code": "CHECKOUT_FAIL",
            },status=status.HTTP_400_BAD_REQUEST)
            data['id']=invoices.id
            return Response({
                "msg":"สร้างรายการสั่งซื้อสำเร็จ",
                "id": data
            },status=200)
        else:
            return Response({
            "code": "CART_EMPTY",
            "msg": "กรุณาเลือกสินค้าใส่ตะกร้า",
            },status=status.HTTP_400_BAD_REQUEST)


class GetMyInvoiceList(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer

    def __init__(self, **kwargs):
        self.response_format = ResponseInfoProduct().response
        super(GetMyInvoiceList, self).__init__(**kwargs)

    def list(self, request, *args, **kwargs):
        response_data = super(GetMyInvoiceList, self).list(request, *args, **kwargs)
        self.response_format["data"] = response_data.data
        self.response_format["status"] = True
        if not response_data.data:
            self.response_format["message"] = "List empty"
        return Response(self.response_format)

class GetMyInvoiceDetail(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    queryset = Invoice.objects.all()
    serializer_class = InvoiceDetailSerializer

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        if serializer.data:
            custom_data = {
                    "status": "ดึงข้อมูลสำเร็จ",
                    "data": serializer.data
            }
            return Response(custom_data)
        else:
            raise NotFound()

    def get_object(self):
        queryset = self.get_queryset()
        try:
            obj =  queryset.get(pk=self.kwargs['pk'])
            
        except:
            raise NotFound()
        return obj



class SubmitVoidInvoice(generics.ListCreateAPIView):
    queryset = Invoice.objects.all()
    serializer_class = InvoiceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            invoices = Invoice.objects.get(id=pk)
        except:
            raise NotFound()
        # data = request.data
        if invoices.status == "Delivered":
            return Response({
                "code": "VOID_INVOICE_FAIL",
                "msg": "ยกเลิกรายการไม่สำเร็จเนื่องจากอยู่ในสถานะ ชำระเงินแล้ว"
            },status=status.HTTP_400_BAD_REQUEST)
        if invoices.status == "Cancel":
            return Response({
                "code": "VOIDED",
                "msg": "รายการสินค้านี้อยู่ในสถานะ 'ยกเลิก' รายการแล้ว"
            },status=status.HTTP_400_BAD_REQUEST)
        invoices.status = "Cancel"
        invoices.save()
        return Response({
            "msg" : "ยกเลิกรายการสำเร็จ",
        },status=status.HTTP_200_OK)