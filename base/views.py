from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from .forms import UserForm, MyUserCreationForm, AddressForm
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
import json
from django.db.models import Q
from .models import Category, Product, Order, Item, Customer, Address
# Create your views here.
def home(request):
    categories_h = Category.objects.all()

    context = {
        'categories_h':categories_h
    }
    return render(request, 'base/home.html', context)

def shop(request):
    q = request.GET.get('q') if request.GET.get('q') != None else ''
    products = Product.objects.filter(
        Q(name__icontains=q) |
        Q(category__title__icontains=q) |
        Q(category__parent__title__icontains=q) |
        Q(description__icontains=q),
        # Q(price__gte=min_price, price__lte=max_price)
    )
    context = {
        'products':products
    }
    return render(request, 'base/shop.html', context)


def loginPage(request):
    page = 'login'
    login_form = UserForm()
    if request.user.is_authenticated:
        return redirect('home')
    if request.method == 'POST':
        messages.success(request, None)
        email = request.POST.get('email').lower()
        password = request.POST.get('password')

        try:
            user = Customer.object.get(email=email)
        except:
            messages.error(request, 'User does not exist')
        user = authenticate(request, email=email, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, "Username and password does not match")

    context = {'page':page, 'login_form':login_form}
    return render(request, 'base/login_register.html', context)


def registerPage(request):
    if request.user.is_authenticated:
        return redirect('home')

    form = MyUserCreationForm()
    if request.method == 'POST':
        form = MyUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.save()
            login(request, user)
            return redirect('home')
        else:
            messages.error(request, 'An error occured during registration')
    return render(request, 'base/login_register.html', {'form':form})


def logoutUser(request):
    logout(request)
    return redirect('home')


def updateItem(request):
    data = json.loads(request.body.decode("utf-8"))
    productId = data['productId']
    action = data['action']

    customer = request.user
    product = Product.objects.get(id=productId)
    order, created = Order.objects.get_or_create(customer=customer, complete=False)

    item, created = Item.objects.get_or_create(order=order, product=product)
    if action == 'add':
        item.quantity = item.quantity + 1
    elif action == 'remove' and item.quantity > 1:
        item.quantity = item.quantity - 1
    elif action == 'delete':
        item.quantity = 0
    item.save()

    if item.quantity <= 0:
        item.delete()

    count = order.item_set.all().count()

    response_data = {
        'order_price':order.order_price,
        'total_price':order.total_price,
        'price':item.item_price,
        'quantity': item.quantity,
        'count':count
    }

    return JsonResponse(response_data, safe=False)


def addressRegister(request):
    if request.method == 'POST':
        address_form = AddressForm(request.POST)
        if address_form.is_valid():
            address = address_form.save(commit=False)
            address.customer = request.user
            address.save()
            return redirect('checkout')
    else:
        address_form = AddressForm()
    context = {
        'address_form':address_form
    }
    return render(request, 'base/checkout.html', context)


@login_required(login_url='login')
def cartPage(request):
    items = None
    order = None
    if request.user.is_authenticated:
        customer = request.user
        try:
            order = Order.objects.get(customer=customer, complete=False)
            items = order.item_set.all()

        except Order.DoesNotExist:
            pass
    order_exists = Order.objects.filter(customer=request.user, complete=False).exists()
    context = {
        'items':items,
        'order':order,
        'order_exists':order_exists
    }

    return render(request, 'base/cart.html', context)


@login_required(login_url='login')
def checkOutPage(request):
    order = None
    items = None   
    addresses = None
    address_form = AddressForm()
    if request.user.is_authenticated:      
        customer = request.user
        try:
            addresses = Address.objects.filter(customer=customer)
            order = Order.objects.get(customer=customer, complete=False)
            items = order.item_set.all()
        except:
            addresses = None
            order = None
        if not order:
            order = Order.objects.create(customer=customer, complete=False)
    
    if request.method == 'POST':
        selected_address_id = request.POST.get('address')
        selected_address = Address.objects.get(pk=selected_address_id)
        if order is not None:
            order.address = selected_address
            order.complete = True
            order.save()
            messages.success(request, 'Order has been placed successfully!')
            return redirect('home')
        else:
            # Handle the case where an Order object does not exist
            messages.error(request, 'You do not have any pending orders.')
            return redirect('checkout')

    address_exists = Address.objects.filter(customer=request.user).exists()
    order_exists = Order.objects.filter(customer=request.user, complete=False).exists()

    context = {       
        'order_exists':order_exists,
        'address_exists':address_exists,
        'items':items,
        'order':order, 
        'addresses':addresses,
        'address_form':address_form
        }

    return render(request, 'base/checkout.html', context)


def productPage(request, pk):
    product = get_object_or_404(Product, id=pk)
    image = product.imageURL
    category = product.category.first()
    context = {
        'category':category,
        'image':image,
        'product':product
    }
    return render(request, 'base/product.html', context)


@login_required(login_url='login')
def orderPage(request):
    orders = None
    orders_p, orders_d, orders_n, orders_t = (0, 0, 0, 0)
    order_exists = False
    if request.user.is_authenticated:
        orders = Order.objects.filter(customer=request.user, complete=True).order_by('-date')
        order_exists = Order.objects.filter(customer=request.user, complete=True).exists()
        orders_p = Order.objects.filter(customer=request.user, complete=False).count()
        orders_d = Order.objects.filter(customer=request.user, complete=True, delivered=True).count()
        orders_n = Order.objects.filter(customer=request.user, complete=True, delivered=False).count()
        orders_t = Order.objects.filter(customer=request.user).count()
    context = {
        'orders_p': orders_p,
        'orders_d': orders_d,
        'orders_n': orders_n,
        'orders_t': orders_t,
        'orders': orders,
        'order_exists': order_exists,
    }
    return render(request, 'base/orders.html', context)


def aboutPage(request):
    return render(request, 'base/about.html')