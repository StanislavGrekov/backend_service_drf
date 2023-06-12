from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth.models import User
from orders.models import Shop, Category, Contact
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token
from rest_framework.response import Response

from orders.signal import create_send_mail, update_send_mail

def get_username(request):
    """Получение id пользователя"""
    if request.user.is_authenticated:
        user_id = request.user.id
        return user_id

class ShopUserSerializer(serializers.ModelSerializer):
    """Сериализатор, для отображения пользователя"""
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']


class UserSerializer(serializers.ModelSerializer):
    """Класс создает, обновляет пользователя и отправляет письма о успешно создании, обновлении"""
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']

    def create(self, validated_data):
        user = super().create(validated_data)
        token = Token.objects.create(user=user)

        create_send_mail(user.email, user.first_name, user.last_name, token)

        return user

    def update(self, instance, validated_data):
        user = super().update(instance, validated_data)

        token_old = Token.objects.get(user=user)
        token_old.delete()

        token_new = Token.objects.create(user=user)
        update_send_mail(user.email, user.first_name, user.last_name, token_new)

        return user


class ContactSerializer(serializers.ModelSerializer):

    class Meta:
        model = Contact
        fields = ['city', 'street', 'house', 'structure', 'building', 'apartment',  'phone', 'user']

    def create(self, validated_data):
        city = validated_data.get('city')
        street = validated_data.get('street')
        house = validated_data.get('house')
        structure = validated_data.get('structure')
        building = validated_data.get('building')
        apartment = validated_data.get('apartment')
        phone = validated_data.get('phone')

        request = self.context['request']
        user_id = get_username(request)

        contact = Contact.objects.create(user_id=user_id, city=city, street=street, house=house, structure=structure,
                                         building=building, apartment=apartment, phone=phone )

        return contact



class CategorySerializer(serializers.Serializer):
    """Cериализатор для создания категорий (почему-то не мог записывать id используя ModelSerializer)"""
    id = serializers.IntegerField()
    name = serializers.CharField()


class ShopSerializer(serializers.ModelSerializer):
    """Класс создает магазин, категории товаров и делает связь между ними"""

    categories = CategorySerializer(many=True)

    class Meta:
        model = Shop
        fields = ['name', 'url', 'user', 'state', 'categories']

    def create(self, validated_data):
        name = validated_data.get('name')
        url = validated_data.get('url') # Адрес магазина
        state = True # Указываем, что магазин активен

        request = self.context['request']
        user_id = get_username(request)

        categories = validated_data.get('categories')

        shop = Shop.objects.create(name=name, url=url, user_id=user_id, state=state)

        for category in categories:
            cat = Category.objects.create(id=category['id'], name=category['name'])
            shop.categories.add(cat)

        return shop



