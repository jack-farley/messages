from rest_framework.exceptions import APIException


class UsernameNotProvided(APIException):
    status_code = 400
    default_detail = 'Must provide a username for the friend you wish to ' \
                     'remove.'
    default_code = 'incomplete_request'


class UsersNotFriends(APIException):
    status_code = 400
    default_detail = 'The user you are trying to unfriend is not on your ' \
                     'friends list.'
    default_code = 'not_friends'


class UsersAlreadyFriends(APIException):
    status_code = 400
    default_detail = 'The user you are trying to send a request to is ' \
                     'already in your friends list.'
    default_code = 'already_friends'


class AlreadyPendingRequest(APIException):
    status_code = 400
    default_detail = 'There is already a pending friend request between you' \
                     'and the user to whom you are sending a request.'
