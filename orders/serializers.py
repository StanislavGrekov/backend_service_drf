from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token



class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email', 'password']

    def save(self, *args, **kwargs):
        # Создаём объект класса User
        try:
            user = User(
                email=self.validated_data['email'], # Назначаем Email
                username=self.validated_data['username'], # Назначаем Логин
                first_name = self.validated_data['first_name'],
                last_name = self.validated_data['last_name'],
                password = self.validated_data['password']
            )
            user.save()
            print(user.username)

            token = Token.objects.create(user=user)
            print(token)

            return user
        except:
            raise ValidationError({'Answer': "Возникла ошибка"})