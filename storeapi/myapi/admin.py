from django.contrib import admin
from .models import Category,Cart,Product,ProductImage,Invoice,Invoice_item
from django.contrib.auth.models import User

class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name','image','detail']

class ProductAdmin(admin.ModelAdmin):
    list_display = ['id','name','category','price','detail','is_enable']

class CartAdmin(admin.ModelAdmin):
    list_display = ['id','user','product','quantity','total']
    list_editable = ['quantity','total']

class InvoiceAdmin(admin.ModelAdmin):
    list_display = ['id','user','created_datetime','updated_datetime','total','status']

class Invoice_itemAdmin(admin.ModelAdmin):
    list_display = ['id','invoice','product','quantity','total','created_datetime']
    

# Register your models here.
admin.site.register(Category,CategoryAdmin)
admin.site.register(Product,ProductAdmin)
admin.site.register(ProductImage)
admin.site.register(Invoice,InvoiceAdmin)
admin.site.register(Invoice_item,Invoice_itemAdmin)
admin.site.register(Cart,CartAdmin)