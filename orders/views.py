from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView
from django.contrib.auth.models import User
from .serializers import UserSerializer, ShopSerializer, ContactSerializer
from orders.models import Shop, Contact
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

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


# class ContactUpdate(UpdateAPIView):
#     """Обновление пользователя"""
#     queryset = Contact.objects.all()
#     serializer_class = ContactSerializer


# Работа с магазином

class ShopCreate(ListCreateAPIView):
    """Создание магазина, заполнение таблиц из прайса"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated,)

class ShopDestroy(DestroyAPIView):
    """Удаление магазина, удаление товаров"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated,)