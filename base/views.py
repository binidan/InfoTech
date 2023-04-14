from django.shortcuts import render
from .models import Category, Product
# Create your views here.
def home(request):
    categories_h = Category.objects.all()

    context = {
        'categories_h':categories_h
    }
    return render(request, 'base/home.html', context)