from rest_framework.exceptions import APIException


class UsernameNotProvided(APIException):
    status_code = 400
    default_detail = 'Must provide a username for the user you wish to add ' \
                     'or remove as a friend.'
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
    default_detail = 'There is already a pending friend request between you ' \
                     'and the user to whom you are sending a request.'
    default_code = 'already_request'


class MissingRequestAccepted(APIException):
    status_code = 400
    default_detail = 'You must set accepted to True to accept the request ' \
                     'or False to reject it. Accepted field is required.'
    default_code = 'missing_response'


class RequestDoesNotExist(APIException):
    status_code = 400
    default_detail = 'No pending request exists with the given parameters.'
    default_code = 'no_request'
