import pytest
from rest_framework.test import APIClient
from rest_framework.authtoken.models import Token
from fixture_data import fixture_user, fixture_contact


@pytest.fixture
def client():
    return APIClient()


@pytest.mark.django_db
def test_user(client):
    username_list = []

    for i, val in enumerate(fixture_user, start=1):

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

        username_list.append(data['username'])

        client.logout()

    print(f'\nTest passed for username: {username_list}')


@pytest.mark.django_db
def test_contact(client):
    contact_data = []
    count_contact = 0

    for i, val in enumerate(fixture_user, start=1):

        # Создаем пользователя
        client.post('/api/usercreate/', val)

        # Получаем токен пользователя, авторизуемся
        token = Token.objects.get(user_id=i)
        client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))

        # Создаем контактные данные
        response = client.post('/api/contact/create/', fixture_contact[count_contact])
        data = response.data
        assert response.status_code == 201
        assert data['city'] == fixture_contact[count_contact]['city']

        # Изменяем контактные данные пользователя
        response = client.patch(f'/api/contact/update/{count_contact+1}/', {"city": "Кайгородово"})
        data = response.data
        assert response.status_code == 200
        assert data['city'] == 'Кайгородово'

        count_contact += 1
        contact_data.append(data)

        client.logout()
    print(f'\nTest passed for contact_data:\n{contact_data}')


@pytest.mark.django_db
def test_shop(client):

    user = {"username": "Semen",
            "first_name": "Семен",
            "last_name": "Иванов",
            "email": "ivanov19@yandex.ru",
            "password": "123456lkldfkdfs"}


    shop = {"name": "Связной",
            "url": "https://raw.githubusercontent.com/StanislavGrekov/my_diplom_drf/master/shop1.yaml"}

    # Создаем пользователя
    client.post('/api/usercreate/', user)

    # Получаем токен пользователя, авторизуемся
    token = Token.objects.get(user_id=1)
    client.credentials(HTTP_AUTHORIZATION='Token ' + str(token))

    # Создаем магазин, загружаем товары из прайса
    response = client.post('/api/shop/create/', shop)
    assert response.status_code == 201

    # Получаем список магазинов
    response = client.get(f'/api/shop/all/')
    assert response.status_code == 200
    data = response.data
    assert data[0]['name'] == shop['name']
