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
