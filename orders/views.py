from django.http import JsonResponse
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.models import User
from orders.filters import ProductFilter

from orders.permissions import get_username, IsAdmin, IsOwner
from orders.signal import order_user_create_send_mail

from .serializers import UserSerializer, ShopSerializer, ContactSerializer, ProductSerializer, CategorySerializers, \
    ShopSerializersFORFilters, OrderSerializer, OrderProcessingSerializer
from orders.models import Shop, Contact, Category, Product, ProductInfo, OrderItem, Order
from django.core.exceptions import ObjectDoesNotExist


########################### Работа с пользователем##################

class UserCreate(ListCreateAPIView):
    """Создание пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserUpdate(UpdateAPIView):
    """Обновление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwner)

class UserDetail(RetrieveAPIView):
    """Информация о пользователе"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

class UserDestroy(DestroyAPIView):
    """Удаление пользователя"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated, IsOwner)

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

class ShopUpdate(UpdateAPIView):
    """Создание обновление магазина"""
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
            return Response({'Answer': "The store has been deleted!"})
        except ObjectDoesNotExist:
            return Response({"Answer": "The store not found!"})

############################### Создание заказа, редактирование, удаление###################

class OrderItemCreate(APIView):
    """Работа с заказами. Просмотр корзины (get), создание заказа(post), удаление заказа(delete)"""
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """ Просмотр корзины пользователя """
        user_id = get_username(request)
        user = User.objects.get(id=user_id)
        contact = Contact.objects.get(user_id=user_id)

        order_dict = {}
        total_cost = 0

        orders = Order.objects.filter(user_id=user_id, state='basket')
        for order in orders:
            orderitem = OrderItem.objects.get(order_id=order.id)
            products = ProductInfo.objects.filter(id=orderitem.product_info_id)
            for product in products:
                order_dict[order.id] = f'external_id:{product.external_id}, model:{product.model}, price:{product.price_rrc}, quantity:{orderitem.quantity}, total_price: {product.price_rrc*orderitem.quantity} rubles.'
                total_cost += product.price_rrc*orderitem.quantity

        order_dict['total_cost']=f'{total_cost} rubles.'

        return JsonResponse({'user': user.username, 'phone': contact.phone, 'orders':order_dict})


    def post(self, request, *args, **kwargs):
        """ Добавление заказа в корзину """

        user_id = get_username(request)
        contact = Contact.objects.get(user_id=user_id)

        serializer = OrderSerializer(data=request.data)

        if serializer.is_valid():
            product_info = ProductInfo.objects.get(external_id=serializer.data['external_id'])
            shop = Shop.objects.get(id=product_info.shop_id)
            if shop.name != serializer.data['shop']:
                return JsonResponse({'Error': 'The store not found!'})
            else:
                if shop.state == True: # Проверка активен ли магазин
                    order = Order.objects.create(state='basket', contact_id=contact.id, user_id=user_id)
                    OrderItem.objects.create(quantity=serializer.data['quantity'], order_id=order.id, product_info_id=product_info.id)
                    return Response({'Answer': 'You order is added, go to basket'})
                else:
                    return JsonResponse({'Error': 'The store is deactivated!'})
        return JsonResponse({'Error': serializer.errors})


    def delete(self, request, pk, format=None):
        """ Удаление заказа из корзины"""
        user_id = get_username(request)

        try:
            order = Order.objects.get(id=pk, user_id=user_id, state='basket')
            OrderItem.objects.get(order_id=order.id).delete()
            order.delete()
            return JsonResponse({'Answer': 'Order deleted!'})
        except ObjectDoesNotExist:
            return JsonResponse({"Error": "The order not found, or you not Owner!"})


############################### Работа со статусом заказа ###################

class OrderProcessing(APIView):
    """ """
    permission_classes = (IsAuthenticated,)

    def get(self, request, *args, **kwargs):
        """ Просмотр заказа пользователя """
        user_id = get_username(request)
        user = User.objects.get(id=user_id)
        contact = Contact.objects.get(user_id=user_id)

        order_dict = {}

        orders = Order.objects.filter(user_id=user_id, state='Confirmed')
        for order in orders:
            orderitem = OrderItem.objects.get(order_id=order.id)
            products = ProductInfo.objects.filter(id=orderitem.product_info_id)
            for product in products:
                order_dict[order.id] = f'Status:{order.state}, model:{product.model},  quantity:{orderitem.quantity}.'

        return Response({'first_name': user.first_name, 'last_name': user.last_name, 'phone': contact.phone, 'orders':order_dict})


    def post(self, request, *args, **kwargs):
        """ Запуск заказа в обработку """

        user_id = get_username(request)
        user = User.objects.get(id=user_id)

        serializer = OrderProcessingSerializer(data=request.data)

        if serializer.is_valid():

            if user.is_staff == False:
                if serializer.data['state'] == 'Confirmed':
                    try:
                        orders_count = Order.objects.filter(user_id=user_id, state='basket').count()
                        if orders_count == 0:
                            return JsonResponse({'Error': 'No orders!'})
                        orders = Order.objects.filter(user_id=user_id, state='basket')
                        for order in orders:
                            order_items = OrderItem.objects.filter(order_id=order.id)
                            for order_item in order_items:
                                product_info = ProductInfo.objects.get(id=order_item.product_info_id)
                                value = product_info.quantity - order_item.quantity
                                ProductInfo.objects.filter(id=order_item.product_info_id).update(quantity=value)

                        Order.objects.filter(user_id=user.id).update(state=serializer.data['state'])

                        superuser=User.objects.get(is_staff=True)

                        order_user_create_send_mail(superuser.email, superuser.username, user) # Послыаем письмо администратору для проверки

                        return JsonResponse({'Answer': 'The order has been sent to work!'})
                    except:
                        return JsonResponse({'Error': 'Not enough products in stock!'})

                elif serializer.data['state'] == 'Delivered':
                    Order.objects.filter(user_id=user.id, state='Sent').update(state=serializer.data['state'])
                    return JsonResponse({'Answer': 'Thank you for using the our service!'})

                else:
                    return JsonResponse({'Error': 'You can not use this state!'})

            else:
                if serializer.data['state'] == 'Sent':
                    Order.objects.filter(user_id=user.id, state='Sent').update(state=serializer.data['state'])
                    return JsonResponse({'Answer': 'Thank you for using the our service!'})

        # if serializer.is_valid():
        #     product_info = ProductInfo.objects.get(external_id=serializer.data['external_id'])
        #     shop = Shop.objects.get(id=product_info.shop_id)
        #     if shop.name != serializer.data['shop']:
        #         return JsonResponse({'Error': 'The store not found!'})
        #     else:
        #         if shop.state == True: # Проверка активен ли магазин
        #             order = Order.objects.create(state='basket', contact_id=contact.id, user_id=user_id)
        #             OrderItem.objects.create(quantity=serializer.data['quantity'], order_id=order.id, product_info_id=product_info.id)
        #             return Response({'Answer': 'You order is added, go to basket'})
        #         else:
        #             return JsonResponse({'Error': 'The store is deactivated!'})
        return JsonResponse({'Error': serializer.errors})


    def delete(self, request, pk, format=None):
        """ Удаление заказа из корзины"""
        user_id = get_username(request)

        try:
            order = Order.objects.get(id=pk, user_id=user_id, state='basket')
            OrderItem.objects.get(order_id=order.id).delete()
            order.delete()
            return JsonResponse({'Answer': 'Order deleted!'})
        except ObjectDoesNotExist:
            return JsonResponse({"Error": "The order not found, or you not Owner!"})

######################  Классы для работы с фильтром (запросы 11-1 - 11-6)##################

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