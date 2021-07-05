from django.db import models
from django.contrib.auth.models import User
import datetime
from versatileimagefield.fields import VersatileImageField, PPOIField

# Create your models here.

class Category(models.Model):
    name = models.CharField(max_length=100)
    image = VersatileImageField(upload_to= 'uploads/',ppoi_field='uploads_ppoi',max_length=200,default=None,null=True,blank=True)
    uploads_ppoi = PPOIField()
    detail = models.CharField(max_length=255)
    is_enable = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class Product(models.Model):
    category = models.ForeignKey(Category,default=None,on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=20, decimal_places=2, help_text='price', default=0)
    detail = models.CharField(max_length=255)
    image = VersatileImageField(upload_to= 'uploads/',ppoi_field='uploads_ppoi',max_length=200,default=None,null=True,blank=True)
    uploads_ppoi = PPOIField()
    is_enable = models.BooleanField(default=True)
    def __str__(self):
        return self.name

class ProductImage(models.Model):
    product = models.ForeignKey(Product,related_name='images',default=None,on_delete=models.CASCADE)
    image = VersatileImageField(upload_to= 'uploads/',ppoi_field='uploads_ppoi',max_length=200,default=None,null=True,blank=True)
    uploads_ppoi = PPOIField()
    def __str__(self):
        return self.product.name

CHOICE_STATUS = (
    ('Wait','wait'),
    ('Delivered','delivered'),
    ('Cancel','cancel')
)

class Invoice(models.Model):
    user = models.ForeignKey(User,related_name='invoices',default=None,on_delete=models.CASCADE)
    created_datetime = models.DateTimeField(auto_now=True)
    updated_datetime = models.DateTimeField(default=None,null=True)
    total = models.IntegerField(default=0)
    status = models.CharField(max_length=10,null=True,blank=True,choices=CHOICE_STATUS,default='Wait')

    def save(self, *args, **kwargs):
            self.updated_datetime = datetime.datetime.now()
            super().save(*args, **kwargs)

    def __str__(self):
        return self.user.username

class Invoice_item(models.Model):
    product = models.ForeignKey(Product,default=None,on_delete=models.CASCADE)
    invoice = models.ForeignKey(Invoice,related_name='invoices_items',default=None,on_delete=models.CASCADE)
    created_datetime = models.DateTimeField(auto_now=True)
    quantity = models.IntegerField(default=0)
    total = models.IntegerField(default=0)
    def __str__(self):
        return self.product.name

class Cart(models.Model):
    product = models.ForeignKey(Product,default=None,on_delete=models.CASCADE)
    user = models.ForeignKey(User,default=None,on_delete=models.CASCADE)
    quantity = models.IntegerField(default=0)
    total = models.DecimalField(max_digits=20, decimal_places=2, help_text='price', default=0)
    
    class Meta:
        unique_together = ['user','product']

    def __str__(self):
        return self.product.name
