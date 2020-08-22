import json
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
        self.user1 = create_user('user1', 'bob', 'smith')
        self.user2 = create_user('user2', 'jim', 'walsh')
        response = self.client.post(
            reverse('accounts:login'),
            data=json.dumps({
                'username': self.user1.username,
                'password': PASSWORD,
            }),
            content_type='application/json'
        )
        self.access1 = response.data['access']
        response = self.client.post(
            reverse('accounts:login'),
            data=json.dumps({
                'username': self.user2.username,
                'password': PASSWORD,
            }),
            content_type='application/json'
        )
        self.access2 = response.data['access']

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
            HTTP_AUTHORIZATION=f'Bearer {self.access1}'
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['username'], self.user1.username)
        self.assertEqual(response.data['first_name'], self.user1.first_name)
        self.assertEqual(response.data['last_name'], self.user1.last_name)

    def test_get_other_profile(self):
        response = self.client.get(
            reverse('profiles:profile',
                    kwargs={'username': self.user2.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access1}'
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['username'], self.user2.username)
        self.assertEqual(response.data['first_name'], self.user2.first_name)
        self.assertEqual(response.data['last_name'], self.user2.last_name)

    def test_update_my_profile(self):
        new_first_name = "jimmy"
        new_last_name = "wallace"
        response = self.client.patch(
            reverse('profiles:profile',
                    kwargs={'username': self.user1.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access1}',
            data=json.dumps({
                "username": "not_bob",
                "first_name": new_first_name,
                "last_name": new_last_name,
            }),
            content_type='application/json'
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(response.data['username'], self.user1.username)
        self.assertEqual(response.data['first_name'], new_first_name)
        self.assertEqual(response.data['last_name'], new_last_name)

    def test_update_other_profile(self):
        new_first_name = "jimmy"
        new_last_name = "wallace"
        response = self.client.patch(
            reverse('profiles:profile',
                    kwargs={'username': self.user2.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access1}',
            data=json.dumps({
                "username": "not_bob",
                "first_name": new_first_name,
                "last_name": new_last_name,
            }),
            content_type='application/json'
        )

        self.assertEqual(status.HTTP_403_FORBIDDEN, response.status_code)


class HttpFriendsTest(APITestCase):

    def setUp(self):
        self.user1 = create_user('user1', 'bob', 'smith')
        response = self.client.post(
            reverse('accounts:login'),
            data=json.dumps({
                'username': self.user1.username,
                'password': PASSWORD,
            }),
            content_type='application/json'
        )
        self.access1 = response.data['access']

        self.user2 = create_user('user2', 'jim', 'walsh')
        response = self.client.post(
            reverse('accounts:login'),
            data=json.dumps({
                'username': self.user2.username,
                'password': PASSWORD,
            }),
            content_type='application/json'
        )
        self.access2 = response.data['access']

        self.user3 = create_user('user3', 'johnny', 'fisher')
        response = self.client.post(
            reverse('accounts:login'),
            data=json.dumps({
                'username': self.user3.username,
                'password': PASSWORD,
            }),
            content_type='application/json'
        )
        self.access3 = response.data['access']

        # Setup Info
        # user1 and user2 are friends.
        # user2 has a pending friend request to user3.
        self.user1.profile.add_friend(self.user2.profile)
        self.user2.profile.send_request(self.user3.profile)

    # Checking user1's friends
    def test_get_friends(self):
        response = self.client.get(
            reverse('profiles:friends',
                    kwargs={'username': self.user1.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access1}'
        )

        friends = response.data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(friends), 1)
        self.assertEqual(friends[0]['username'], self.user2.username)
        self.assertEqual(friends[0]['first_name'], self.user2.first_name)
        self.assertEqual(friends[0]['last_name'], self.user2.last_name)

    # Testing user1 sending a friend request to user3
    def test_send_request(self):
        response = self.client.post(
            reverse('profiles:friends',
                    kwargs={'username': self.user1.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access1}',
            data=json.dumps({
                "username": f"{self.user3.username}"
            }),
            content_type='application/json'
        )

        request = response.data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(request['from_user'], self.user1.username)
        self.assertEqual(request['to_user'], self.user3.username)
        self.assertEqual(request['status'], 3)

        # Check that user3 has an incoming request
        response2 = self.client.get(
            reverse('profiles:requests',
                    kwargs={'username': self.user3.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access3}'
        )

        # should already have a request from user 2
        incoming_requests = response2.data
        self.assertEqual(status.HTTP_200_OK, response2.status_code)
        self.assertEqual(len(incoming_requests), 2)
        self.assertEqual(incoming_requests[1]['from_user'],
                         self.user1.username)
        self.assertEqual(incoming_requests[1]['to_user'], self.user3.username)
        self.assertEqual(incoming_requests[1]['status'], 3)

        # Check that user1 has it as an outgoing request
        response3 = self.client.get(
            reverse('profiles:requests',
                    kwargs={'username': self.user1.username}),
            data={'outgoing': '1'},
            HTTP_AUTHORIZATION=f'Bearer {self.access1}',
        )

        outgoing_requests = response3.data
        self.assertEqual(status.HTTP_200_OK, response3.status_code)
        self.assertEqual(len(outgoing_requests), 1)
        self.assertEqual(outgoing_requests[0]['from_user'],
                         self.user1.username)
        self.assertEqual(outgoing_requests[0]['to_user'], self.user3.username)
        self.assertEqual(outgoing_requests[0]['status'], 3)

    # Check that user2 has an outgoing request to user3
    def test_get_outgoing_requests(self):
        response = self.client.get(
            reverse('profiles:requests',
                    kwargs={'username': self.user2.username}),
            data={'outgoing': '1'},
            HTTP_AUTHORIZATION=f'Bearer {self.access2}',
        )

        outgoing_requests = response.data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(outgoing_requests), 1)
        self.assertEqual(outgoing_requests[0]['from_user'],
                         self.user2.username)
        self.assertEqual(outgoing_requests[0]['to_user'], self.user3.username)
        self.assertEqual(outgoing_requests[0]['status'], 3)

    # Check that user3 has an incoming request from user2
    def test_get_incoming_requests(self):
        response = self.client.get(
            reverse('profiles:requests',
                    kwargs={'username': self.user3.username}),
            data={'outgoing': '0'},
            HTTP_AUTHORIZATION=f'Bearer {self.access3}',
        )
        incoming_requests = response.data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(incoming_requests), 1)
        self.assertEqual(incoming_requests[0]['from_user'],
                         self.user2.username)
        self.assertEqual(incoming_requests[0]['to_user'], self.user3.username)
        self.assertEqual(incoming_requests[0]['status'], 3)

    # Check that user3 can accept the request from user2,
    # check that they are friends
    def test_accept_request(self):
        response = self.client.post(
            reverse('profiles:requests',
                    kwargs={'username': self.user3.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access3}',
            data=json.dumps({
                "username": f"{self.user2.username}",
                "accepted": True
            }),
            content_type='application/json'
        )

        request = response.data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(request['from_user'], self.user2.username)
        self.assertEqual(request['to_user'], self.user3.username)
        self.assertEqual(request['status'], 1)

        # Check that user2 is friends with user3
        response2 = self.client.get(
            reverse('profiles:friends',
                    kwargs={'username': self.user2.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access2}'
        )

        friends = response2.data
        self.assertEqual(status.HTTP_200_OK, response2.status_code)
        self.assertEqual(len(friends), 2)
        self.assertEqual(friends[1]['username'], self.user3.username)
        self.assertEqual(friends[1]['first_name'], self.user3.first_name)
        self.assertEqual(friends[1]['last_name'], self.user3.last_name)

        # Check that user3 is friends with user2
        response3 = self.client.get(
            reverse('profiles:friends',
                    kwargs={'username': self.user3.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access3}'
        )

        friends = response3.data
        self.assertEqual(status.HTTP_200_OK, response3.status_code)
        self.assertEqual(len(friends), 1)
        self.assertEqual(friends[0]['username'], self.user2.username)
        self.assertEqual(friends[0]['first_name'], self.user2.first_name)
        self.assertEqual(friends[0]['last_name'], self.user2.last_name)

    # Check that user3 can decline the request from user2,
    # make sure that they are not friends
    def test_decline_request(self):
        response = self.client.post(
            reverse('profiles:requests',
                    kwargs={'username': self.user3.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access3}',
            data=json.dumps({
                "username": f"{self.user2.username}",
                "accepted": False
            }),
            content_type='application/json'
        )

        request = response.data
        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(request['from_user'], self.user2.username)
        self.assertEqual(request['to_user'], self.user3.username)
        self.assertEqual(request['status'], 2)

        # Check that user2 is not friends with user3
        response2 = self.client.get(
            reverse('profiles:friends',
                    kwargs={'username': self.user2.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access2}'
        )

        friends = response2.data
        self.assertEqual(status.HTTP_200_OK, response2.status_code)
        self.assertEqual(len(friends), 1)
        self.assertEqual(friends[0]['username'], self.user1.username)
        self.assertEqual(friends[0]['first_name'], self.user1.first_name)
        self.assertEqual(friends[0]['last_name'], self.user1.last_name)

        # Check that user3 is not friends with user2
        response3 = self.client.get(
            reverse('profiles:friends',
                    kwargs={'username': self.user3.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access3}'
        )

        friends = response3.data
        self.assertEqual(status.HTTP_200_OK, response3.status_code)
        self.assertEqual(len(friends), 0)

    # Check that user1 can remove user2 as a friend,
    # make sure they are no longer friends
    def test_remove_friends(self):
        response = self.client.delete(
            reverse('profiles:friends',
                    kwargs={'username': self.user1.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access1}',
            data=json.dumps({
                "username": f"{self.user2.username}",
            }),
            content_type='application/json'
        )
        self.assertEqual(status.HTTP_204_NO_CONTENT, response.status_code)

        # check that user1 is not friend with user2
        response = self.client.get(
            reverse('profiles:friends',
                    kwargs={'username': self.user1.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access1}'
        )

        self.assertEqual(status.HTTP_200_OK, response.status_code)
        self.assertEqual(len(response.data), 0)

        # check that user2 is not friend with user1
        response2 = self.client.get(
            reverse('profiles:friends',
                    kwargs={'username': self.user2.username}),
            HTTP_AUTHORIZATION=f'Bearer {self.access2}'
        )

        self.assertEqual(status.HTTP_200_OK, response2.status_code)
        self.assertEqual(len(response2.data), 0)

    def test_cancel_request(self):
        pass  # TODO


# TODO:
# 1. test_cancel_request

class HttpBlockingTest(APITestCase):

    def setUp(self):
        pass  # TODO

    def test_get_blocking(self):
        pass  # TODO

    def test_block(self):
        pass  # TODO

    def test_block_end_friendship(self):
        pass  # TODO

    def test_block_end_requests(self):
        pass  # TODO

    def test_blocked_profile_search(self):
        pass  # TODO

    def test_blocked_friend_request(self):
        pass  # TODO

    def test_blocked_block(self):
        pass  # TODO

    def test_unblock(self):
        pass  # TODO

# TODO:
# 1. Blocking tests.
