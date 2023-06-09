from rest_framework import serializers
from rest_framework.serializers import ValidationError
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.authtoken.models import Token

from orders.signal import create_send_mail, update_send_mail

class UserSerializer(serializers.ModelSerializer):
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


