import json
import base64
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.reverse import reverse
from rest_framework.test import APITestCase

PASSWORD = 'password1'


def create_user(username='user7', password=PASSWORD):
    return get_user_model().objects.create_user(
        username=username,
        first_name='John',
        last_name='Smith',
        password=password
    )


class AuthenticationTest(APITestCase):
    def test_sign_up(self):
        response = self.client.post(reverse('accounts:sign-up'), data={
            'username': 'user5',
            'first_name': 'John',
            'last_name': 'Smith',
            'password1': PASSWORD,
            'password2': PASSWORD,
        })
        user = get_user_model().objects.last()
        self.assertEqual(status.HTTP_201_CREATED, response.status_code)
        self.assertEqual(response.data['id'], user.id)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['first_name'], user.first_name)
        self.assertEqual(response.data['last_name'], user.last_name)

    def test_login(self):
        user = create_user()
        response = self.client.post(reverse('accounts:login'), data={
            'username': user.username,
            'password': PASSWORD,
        })

        access = response.data['access']
        header, payload, signature = access.split('.')
        decoded_payload = base64.b64decode(f'{payload}==')
        payload_data = json.loads(decoded_payload)

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertIsNotNone(response.data['refresh'])
        self.assertEqual(payload_data['id'], user.id)
        self.assertEqual(payload_data['username'], user.username)
        self.assertEqual(payload_data['first_name'], user.first_name)
        self.assertEqual(payload_data['last_name'], user.last_name)
