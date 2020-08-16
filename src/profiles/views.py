from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .shortcuts import get_profile_or_404, get_other_profile
from .serializers import ProfileSerializer, RequestSerializer
from .exceptions import (
    UsersNotFriends,
    UsersAlreadyFriends,
    AlreadyPendingRequest,
    MissingRequestAccepted,
    RequestDoesNotExist,
)


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, username):
        return get_profile_or_404(username)

    def get(self, request, username=None, format=None):
        profile = self.get_object(username)

        if self.request.user.profile == profile:
            fields = ProfileSerializer.PRIVATE_FIELDS
        else:
            fields = ProfileSerializer.PUBLIC_FIELDS

        serializer = ProfileSerializer(profile, fields=fields)
        return Response(serializer.data)

    def patch(self, request, username=None, format=None):
        profile = self.get_object(username)

        if profile != request.user.profile:
            raise PermissionDenied

        serializer = ProfileSerializer(instance=profile, data=request.data,
                                       partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class FriendsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, username):
        return get_profile_or_404(username)

    def get(self, request, username=None, format=None):
        profile = self.get_object(username)

        fields = ProfileSerializer.PRIVATE_FIELDS

        queryset = profile.get_friends()

        serializer = ProfileSerializer(queryset, many=True, fields=fields)

        return Response(serializer.data)

    def post(self, request, username=None, format=None):
        profile = self.get_object(username)

        if profile != request.user.profile:
            raise PermissionDenied

        other_profile = get_other_profile(request)

        if profile.is_friends_with(other_profile):
            raise UsersAlreadyFriends

        if profile.has_pending_request_from(other_profile) \
                or profile.has_pending_request_to(other_profile):
            raise AlreadyPendingRequest

        request = profile.send_request(other_profile)
        serializer = RequestSerializer(instance=request)
        return Response(serializer.data, status=status.HTTP_200_OK)

    def delete(self, request, username=None, format=None):
        profile = self.get_object(username)

        if profile != request.user.profile:
            raise PermissionDenied

        other_profile = get_other_profile(request)

        if profile.is_friends_with(other_profile):
            profile.remove_friend(other_profile)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise UsersNotFriends


class RequestsView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, username):
        return get_profile_or_404(username)

    def get(self, request, username=None, format=None):
        profile = self.get_object(username)

        if profile != request.user.profile:
            raise PermissionDenied

        outgoing = request.data.get('outgoing', False)

        if outgoing:
            queryset = profile.get_outgoing_pending()
        else:
            queryset = profile.get_incoming_pending()

        serializer = RequestSerializer(queryset, many=True)

        return Response(serializer.data)

    def post(self, request, username=None, format=None):
        profile = self.get_object(username)

        if profile != request.user.profile:
            raise PermissionDenied

        other_profile = get_other_profile(request)

        if profile.has_pending_request_from(other_profile):

            # Get accepted field
            accepted = request.data.get('accepted', None)
            if accepted is None:
                raise MissingRequestAccepted

            # Approve or deny the request
            if accepted:
                request = profile.approve_request(other_profile)
            else:
                request = profile.deny_request(other_profile)

            # Send response
            if request is None:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = RequestSerializer(request)
            return Response(serializer.data)

        raise RequestDoesNotExist

    def delete(self, request, username=None, format=None):
        profile = self.get_object(username)

        if profile != request.user.profile:
            raise PermissionDenied

        other_profile = get_other_profile(request)

        if profile.has_pending_request_to(other_profile):

            # Cancel the request
            request = profile.cancel_request(other_profile)

            # Send response
            if request is None:
                return Response(status=status.HTTP_500_INTERNAL_SERVER_ERROR)

            serializer = RequestSerializer(request)
            return Response(serializer.data)

        raise RequestDoesNotExist
