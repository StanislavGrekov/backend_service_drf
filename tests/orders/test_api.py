import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User

@pytest.fixture
def client():
    return APIClient()

fixture = [{"username": "Semenov",
            "first_name": "Семен",
            "last_name": "Семенов",
            "email": "stas.ik1987@yandex.ru",
            "password": "123456lkldfkdfs"},

           {"username": "Sema",
            "first_name": "Семен",
            "last_name": "Семенов",
            "email": "st.ik1987@yandex.ru",
            "password": "123456lkldfkdfs"}]

@pytest.mark.django_db
def test_create_user(client):
    for i, val in enumerate(fixture, start=1):
        # Создаем пользователя
        response = client.post('/api/usercreate/', val)
        assert response.status_code == 201

        # Получаем пользователя
        token = Token.objects.get(user_id=i)
        client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))
        response = client.get(f'/api/user/{i}/')
        assert response.status_code == 200

        data = response.data
        assert data['username'] == val['username']

        # Изменяем пользователя
        response = client.patch(f'/api/user/{i}/', {'password': '123'})
        data = response.data
        assert data['password'] == '123'

        # Удаляем пользователя
        token = Token.objects.get(user_id=int(i))
        client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))
        response = client.delete(f'/api/user/{i}/')
        assert response.status_code == 204

        client.logout()

