"""
URL configuration for diplom_drf project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
from rest_framework.authtoken.views import obtain_auth_token

from orders.views import UserList, UserCreate, UserDetail, UserUpdate, UserDestroy, ShopCreate, \
    ShopDestroy, ContactCreate, ContactUpdate, ListProductView, ListProductDateView, ListCategoryView, ListShopView, OrderItemCreate
    # hello_world




urlpatterns = [
    path('admin/', admin.site.urls),
    #Пути для работы с пользователем
    path('api/user/list/', UserList.as_view()),
    path('api/user/create/', UserCreate.as_view()),
    path('api/user/update/<int:pk>/', UserUpdate.as_view()),
    path('api/user/detail/<int:pk>/', UserDetail.as_view()),
    path('api/user/delete/<int:pk>/', UserDestroy.as_view()),

    # Пути для работы с контактом
    path('api/contact/create/', ContactCreate.as_view()),
    path('api/contact/update/<int:pk>/', ContactUpdate.as_view()),

    # Пути для создания/удаления магазина
    path('api/shop/create/', ShopCreate.as_view()),
    path('api/shop/delete/<int:pk>/', ShopDestroy.as_view()),

    # Пути для получения и фильтрации товара
    path('api/product/list/', ListProductView.as_view()), # Список товара
    path('api/product/list/date/', ListProductDateView.as_view()), # Фильтр по дате
    path('api/category/list/', ListCategoryView.as_view()), # Фильтр по категориям
    path('api/shop/list/', ListShopView.as_view()), # Фильтр по магазинам

    # Пути для создания заказа
    path('api/basket/list/', OrderItemCreate.as_view()), # Просмотр корзины
    path('api/basket/add/', OrderItemCreate.as_view()),
]
