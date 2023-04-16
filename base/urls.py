from django.urls import path
from .import views

urlpatterns = [
    path('', views.home, name="home"),
    path('shop/', views.shop, name="shop"),
    path('update-item/', views.updateItem, name="update-item"),
    path('login/', views.loginPage, name="login"),
    path('register/', views.registerPage, name="register"),
    path('address-register', views.addressRegister, name="address-register"),
    path('logout/', views.logoutUser, name="logout"),
    path('cart/', views.cartPage, name="cart"),
    path('checkout/', views.checkOutPage, name="checkout"),
    path('product/<str:pk>/', views.productPage, name="product"),
    path('orders/', views.orderPage, name="orders"),
    path('about/', views.aboutPage, name="about"),
]