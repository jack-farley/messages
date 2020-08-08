from rest_framework.test import APITestCase
from django.contrib.auth import get_user_model
from rest_framework.reverse import reverse

PASSWORD = 'password1'

def create_user(username='user', password=PASSWORD):
    return get_user_model().objects.create_user(
        username=username,
        first_name='John',
        last_name='Smith',
        password=password
    )


class HttpProfileTest(APITestCase):
    def setUp(self):
        user1 = create_user('user1')
        user2 = create_user('user2')
        response = self.client.post(reverse('accounts:login'), data={
            'username': user1.username,
            'password': PASSWORD,
        })
        self.access = response.data['access']


    # def test_send_friend_request(self):
    #
    #
    # def test_accept_friend_request(self):
    #
    #
    # def test_list_friends(self):

