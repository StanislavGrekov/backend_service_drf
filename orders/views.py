from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from orders.permissions import IsOwner
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.models import User
from orders.serializers import get_username

from .serializers import UserSerializer, ShopSerializer, ContactSerializer
from orders.models import Shop, Contact, Category, Product



class Index(APIView):
    permission_classes = (IsAuthenticated,)
    def get(self, request):
        content = {'message': 'Hello, World!'}
        return Response(content)

# Работа с пользователем

class UserList(ListAPIView):
    "Получение списка пользователей"
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserCreate(ListCreateAPIView):
    """Создание пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdate(UpdateAPIView):
    """Обновление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

class UserDetail(RetrieveAPIView):
    """Информация о пользователе"""
    queryset = User.objects.all()
    serializer_class = UserSerializer

class UserDestroy(DestroyAPIView):
    """Удаление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

# Работа с контактом

class ContactCreate(ListCreateAPIView):
    """Создание пользователя"""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticated,)

# Работа с магазином

class ShopCreate(ListCreateAPIView):
    """Создание магазина, заполнение таблиц из прайса"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated,)


class ShopDestroy(APIView):
    """Удаление магазина и всех товаров"""

    def delete(self, request, pk=None):
        shops = Shop.objects.filter(id=pk)
        if not shops:
            return Response({"Ответ": "Магазин не найден!"})
        else:
            for shop in shops:
                categories = Category.objects.filter(shops=shop.id)
                for cat in categories:
                    Product.objects.filter(category_id=cat.id).delete()
                categories.delete()
            shops.delete()
            return Response({'Ответ': "Магазин и все сопутствующие товары удалены!"})
