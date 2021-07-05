from django.urls import include,path
from rest_framework import routers
from django.conf.urls.static import static
from django.conf import settings
from . import views
from .models import Category,Cart,Product,ProductImage,Invoice,Invoice_item
from rest_framework.urlpatterns import format_suffix_patterns
from rest_framework import renderers
from .views import TokenObtainPairView,TokenRefreshView



urlpatterns = format_suffix_patterns([
    path('',views.api_root),
    path('api-auth/', include('rest_framework.urls')),
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', views.Register.as_view(),name='register'),
    path('category/', views.GetCategoryList.as_view(),name='category-list'),
    path('category/<int:pk>/', views.GetCategoryDetail.as_view(),name='category-detail'),
    path('product/', views.GetProductList.as_view(),name='product-list'),
    path('product/<int:pk>/', views.GetProductDetail.as_view(),name='product-detail'),
    path('cart/', views.AddtoCart.as_view(),name='cart-list'),
    path('cart/<int:pk>/', views.EditCartQuanlity.as_view(),name='cart-id'),
    path('checkout/', views.Checkout.as_view(),name='checkout'),
    path('invoice/', views.GetMyInvoiceList.as_view(),name='invoice'),
    path('invoice/<int:pk>/', views.GetMyInvoiceDetail.as_view(),name='invoice-detail'),
    path('invoice/<int:pk>/void/', views.SubmitVoidInvoice.as_view(),name='void'),
    ]) + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)