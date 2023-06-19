from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.parsers import JSONParser
from rest_framework.renderers import JSONRenderer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.models import User
from orders.filters import ProductFilter
from rest_framework import serializers, status
from ujson import loads as load_json


from .serializers import UserSerializer, ShopSerializer, ContactSerializer, ProductSerializer, CategorySerializers, \
    ShopSerializersFORFilters, OrderSerializer
from orders.models import Shop, Contact, Category, Product, ProductInfo, OrderItem, Order
from django.core.exceptions import ObjectDoesNotExist


########################### Работа с пользователем##################

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

############################# Работа с контактом#####################

class ContactCreate(ListCreateAPIView):
    """Создание контакта"""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticated,)

class ContactUpdate(UpdateAPIView):
    """Обновление контакта"""
    queryset = Contact.objects.all()
    serializer_class = ContactSerializer
    permission_classes = (IsAuthenticated,)


############################### Работа с магазином##########################

class ShopCreate(ListCreateAPIView):
    """Создание магазина, заполнение таблиц из прайса"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializer
    permission_classes = (IsAuthenticated,)


class ShopDestroy(APIView):
    """Удаление магазина и всех товаров"""

    permission_classes = (IsAuthenticated,)

    def delete(self, request, pk=None):
        try:
            shop = Shop.objects.get(id=pk)
            categories = Category.objects.filter(shops=shop.id)
            for cat in categories:
                Product.objects.filter(category_id=cat.id).delete()
            categories.delete()
            shop.delete()
            return Response({'Ответ': "Магазин и все сопутствующие товары удалены!"})
        except ObjectDoesNotExist:
            return Response({"Ответ": "Магазин не найден!"})

############################### Работа с заказами###################


# @api_view(['GET', 'POST'])
# def hello_world(request):
#     if request.method == 'GET':
#         basket = OrderItem.objects.all()
#
#         serializer = OrderItemSerializer(basket, many=True)
#
#         return Response(serializer.data)
#
#     if request.method == 'POST':
#
#         serializer_class = OrderItemSerializer
#         serializer = serializer_class(data=request.data)
#         print(request.data)
#         if serializer.is_valid():
#             quantity = serializer.data.get('quantity')
#
#             return Response({"message": "Got some data!", "data": quantity})
#
#         return Response({"message": "Hello, world!"})

class OrderItemCreate(ListCreateAPIView):
    """  """
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    permission_classes = (IsAuthenticated,)

# class OrderItemCreate(APIView):
#     def get(self, request, *args, **kwargs):
#
#         order = Order.objects.all()
#         serializer = OrderSerializer(order, many=True)
#
#         return Response(serializer.data)
#     #
#     def post(self, request, *args, **kwargs):
#         '''
#
#         '''
#         serializer_class = OrderSerializer
#         serializer = serializer_class(data=request.data)
#
#         if serializer.is_valid():
#             state = serializer.data.get('state')
#             return Response({"message": "Got some data!", "data": state})
#
#         return Response({'Status': False, 'Errors': 'Errors'})


        # items_sting = request.data.get('username')
        #
        # print(items_sting)
        #
        #
        # data = JSONParser().parse(request)
        #
        # print(data)
        #

       # order = request.data.get('order')
        # product_info = request.data.get('product_info')
        # quantity = request.data.get('quantity')
        #
        # print(order, product_info, quantity)

        # items_sting = request.data.get('items')
        # if items_sting:
        #     try:
        #         items_dict = load_json(items_sting)
        #         print(items_dict)
        #     except ValueError:
        #         return JsonResponse({'Status': False, 'Errors': 'Неверный формат запроса'})


    # serializer_class = OrderItemSerializer
    #
    # def post(self, request, format=None):
    #
    #     serializer = self.serializer_class(data=request.data)
    #
    #     if serializer.is_valid():
    #         order = serializer.data.get('order')
    #         product_info = serializer.data.get('product_info')
    #         quantity = serializer.data.get('quantity')
    #         element = OrderItem(order=order, product_info=product_info,quantity=quantity )
    #         element.save()
    #         return Response(status=status.HTTP_201_CREATED)
    #
    #     print(serializer.errors)
    #     return Response({'Bad Request': "Invalid Data..."}, status=status.HTTP_400_BAD_REQUEST)


###################### Классы для работы с товаром. Получение товара и фильтрация##################

class ListProductView(ListAPIView):
    """Список товаров, фильтрацией по модели и цене"""
    queryset = ProductInfo.objects.all()
    serializer_class = ProductSerializer
    permission_classes = (IsAuthenticated,)

    filter_backends = [SearchFilter,]
    search_fields = ['model', 'price_rrc']
    ordering_filds = ['time_create']


class ListProductDateView(ListAPIView):
    """Фильтрация по дате"""
    queryset = ProductInfo.objects.all()
    serializer_class = ProductSerializer

    permission_classes = (IsAuthenticated,)
    filterset_class = ProductFilter

class ListCategoryView(ListAPIView):
    """Фильтрация по категориям"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializers
    permission_classes = (IsAuthenticated,)

    filter_backends = [SearchFilter,]
    search_fields = ['name',]

class ListShopView(ListAPIView):
    """Фильтрация по Магазину"""
    queryset = Shop.objects.all()
    serializer_class = ShopSerializersFORFilters
    permission_classes = (IsAuthenticated,)

    filter_backends = [SearchFilter,]
    search_fields = ['name',]