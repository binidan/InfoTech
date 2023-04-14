from django.contrib import admin
from .models import Customer, Address, Product, Order, Item, Category

# Register your models here.
admin.site.register(Customer)
admin.site.register(Category)
admin.site.register(Address)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(Item)

