from django.contrib import admin
from .models import Product,Comment,Bid

# Register your models here.
admin.site.register(Comment)
admin.site.register(Product)
admin.site.register(Bid)



