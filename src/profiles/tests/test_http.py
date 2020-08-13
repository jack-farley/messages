from rest_framework.test import APITestCase
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse

PASSWORD = 'password1'


def create_user(username='user', first_name='John', last_name='Smith',
                password=PASSWORD):
    return get_user_model().objects.create_user(
        username=username,
        first_name=first_name,
        last_name=last_name,
        password=password
    )


class HttpProfileTest(APITestCase):
    def setUp(self):
        user1 = create_user('user1', 'bob', 'smith')
        user2 = create_user('user2', 'jim', 'walsh')
        response = self.client.post(reverse('accounts:login'), data={
            'username': user1.username,
            'password': PASSWORD,
        })
        self.user1 = user1
        self.user2 = user2
        self.access = response.data['access']

    def test_get_profile_unauthorized(self):
        response = self.client.get(
            reverse('profiles:profile',
                    kwargs={'username': self.user1.username}),
        )
        self.assertEqual(status.HTTP_401_UNAUTHORIZED, response.status_code)

    def test_get_my_profile(self):
        response = self.client.get(
            reverse('profiles:profile',
                    kwargs={'username': self.user1.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access}'
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['username'], self.user1.username)
        self.assertEqual(response.data['first_name'], self.user1.first_name)
        self.assertEqual(response.data['last_name'], self.user1.last_name)

    def test_get_other_profile(self):
        other_user = self.user2
        response = self.client.get(
            reverse('profiles:profile',
                    kwargs={'username': other_user.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access}'
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['username'], other_user.username)
        self.assertEqual(response.data['first_name'], other_user.first_name)
        self.assertEqual(response.data['last_name'], other_user.last_name)

    def test_update_my_profile(self):
        user = self.user1
        new_first_name = "jimmy"
        new_last_name = "wallace"
        response = self.client.patch(
            reverse('profiles:profile', kwargs={'username': user.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access}',
            data={
                "username": "not_bob",
                "first_name": new_first_name,
                "last_name": new_last_name,
            }
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['username'], user.username)
        self.assertEqual(response.data['first_name'], new_first_name)
        self.assertEqual(response.data['last_name'], new_last_name)

    def test_update_other_profile(self):
        other_user = self.user2
        new_first_name = "jimmy"
        new_last_name = "wallace"
        response = self.client.patch(
            reverse('profiles:profile',
                    kwargs={'username': other_user.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access}',
            data={
                "username": "not_bob",
                "first_name": new_first_name,
                "last_name": new_last_name,
            }
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)

    # def test_send_friend_request(self):
    #
    #
    # def test_accept_friend_request(self):
    #
    #
    # def test_list_friends(self):
