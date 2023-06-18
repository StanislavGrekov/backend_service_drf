from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.generics import ListAPIView, ListCreateAPIView, RetrieveAPIView, UpdateAPIView, DestroyAPIView, RetrieveUpdateDestroyAPIView
from django.contrib.auth.models import User
# from orders.filters import ProductFilter



from .serializers import UserSerializer, ShopSerializer, ContactSerializer, ProductSerializer, CategorySerializers, \
    ShopSerializersFORFilters, ArticleSerializer
from orders.models import Shop, Contact, Category, Product, ProductInfo
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

class CreateOrderItem(APIView):
    """Создание единицы заказа"""

    permission_classes = (IsAuthenticated,)

    def post(self, request):

        article = request.data.get('articles')

        serializer = ArticleSerializer(data=article)
        if serializer.is_valid(raise_exception=True):
            print(article)

        return Response({"Ответ": "Магазин не найден!"})








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
    # filterset_class = ProductFilter

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