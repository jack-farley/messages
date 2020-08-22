from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .shortcuts import check_my_profile, get_other_profile
from .serializers import ProfileSerializer, RequestSerializer
from .exceptions import (
    UsersNotFriends,
    UsersAlreadyFriends,
    AlreadyPendingRequest,
    MissingRequestAccepted,
    RequestDoesNotExist,
    BlockingUser,
    AlreadyBlocking,
    NotBlocking,
    InvalidURL,
)


# Getting profiles and updating your own

class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username=None, format=None):
        my_profile = self.request.user.profile
        requested_profile = get_other_profile(my_profile, username)

        if requested_profile != my_profile:
            fields = ProfileSerializer.PUBLIC_FIELDS
        else:
            fields = ProfileSerializer.PRIVATE_FIELDS

        serializer = ProfileSerializer(requested_profile, fields=fields)
        return Response(serializer.data)

    def patch(self, request, username=None, format=None):
        my_profile = check_my_profile(self.request.user.profile, username)

        serializer = ProfileSerializer(instance=my_profile,
                                       data=request.data,
                                       partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Getting and removing friends, and sending friend requests

class FriendsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username=None, format=None):
        my_profile = self.request.user.profile
        requested_profile = get_other_profile(my_profile, username)

        queryset = requested_profile.get_friends()
        filtered_queryset = my_profile.filter_blockers(queryset)

        serializer = ProfileSerializer(filtered_queryset, many=True,
                                       fields=ProfileSerializer.PUBLIC_FIELDS)

        return Response(serializer.data)

    def post(self, request, username=None, format=None):
        my_profile = check_my_profile(self.request.user.profile, username)
        other_profile = \
            get_other_profile(my_profile, request.data.get('username', None))

        if my_profile.is_blocking(other_profile):
            raise BlockingUser

        if my_profile.is_friends_with(other_profile):
            raise UsersAlreadyFriends

        if my_profile.has_pending_request_from(other_profile) \
                or my_profile.has_pending_request_to(other_profile):
            raise AlreadyPendingRequest

        request = my_profile.send_request(other_profile)
        serializer = RequestSerializer(instance=request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, username=None, format=None):
        my_profile = check_my_profile(self.request.user.profile, username)
        other_profile = \
            get_other_profile(my_profile, request.data.get('username', None))

        if my_profile.is_friends_with(other_profile):
            my_profile.remove_friend(other_profile)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise UsersNotFriends


# Getting incoming and outgoing requests, responding to them, and canceling
# outgoing requests

class RequestsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username=None, format=None):
        my_profile = check_my_profile(self.request.user.profile, username)

        outgoing_param = request.query_params.get('outgoing', '0')
        if outgoing_param == '1':
            outgoing = True
        elif outgoing_param == '0':
            outgoing = False
        else:
            raise InvalidURL

        if outgoing is True:
            queryset = my_profile.get_outgoing_pending()
        else:
            queryset = my_profile.get_incoming_pending()

        serializer = RequestSerializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request, username=None, format=None):
        my_profile = check_my_profile(self.request.user.profile, username)
        other_profile = \
            get_other_profile(my_profile, request.data.get('username', None))

        if my_profile.has_pending_request_from(other_profile):

            # Get accepted field
            accepted = request.data.get('accepted', None)
            if accepted is None:
                raise MissingRequestAccepted

            # Approve or deny the request
            if accepted:
                request = my_profile.approve_request(other_profile)
            else:
                request = my_profile.deny_request(other_profile)

            # Send response
            if request is None:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = RequestSerializer(request)
            return Response(serializer.data)

        raise RequestDoesNotExist

    def delete(self, request, username=None, format=None):
        my_profile = check_my_profile(self.request.user.profile, username)
        other_profile = \
            get_other_profile(my_profile, request.data.get('username', None))

        if my_profile.has_pending_request_to(other_profile):

            # Cancel the request
            request = my_profile.cancel_request(other_profile)

            # Send response
            if request is None:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = RequestSerializer(request)
            return Response(serializer.data)

        raise RequestDoesNotExist


class BlockingView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, username, format=None):
        my_profile = check_my_profile(self.request.user.profile, username)

        queryset = my_profile.filter_blockers(my_profile.get_blocking())

        serializer = ProfileSerializer(queryset, many=True,
                                       fields=ProfileSerializer.PUBLIC_FIELDS)

        return Response(serializer.data)

    def post(self, request, username, format=None):
        my_profile = check_my_profile(self.request.user.profile, username)
        other_profile = \
            get_other_profile(my_profile, request.data.get('username', None))

        if my_profile.is_blocking(other_profile):
            raise AlreadyBlocking

        my_profile.block(other_profile)

        return Response(status=status.HTTP_204_NO_CONTENT)

    def delete(self, request, username, format=None):

        my_profile = check_my_profile(self.request.user.profile, username)
        other_profile = \
            get_other_profile(my_profile, request.data.get('username', None))

        if not my_profile.is_blocking(other_profile):
            raise NotBlocking

        my_profile.unblock(other_profile)

        return Response(status=status.HTTP_204_NO_CONTENT)
