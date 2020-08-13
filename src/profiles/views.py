from django.core.exceptions import PermissionDenied
from django.http import Http404

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .shortcuts import get_profile_or_404
from .serializers import ProfileSerializer
from .exceptions import UsernameNotProvided, UsersNotFriends


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

    def delete(self, request, username=None, format=None):
        profile = self.get_object(username)

        if profile != request.user.profile:
            raise PermissionDenied

        other_username = request.data.get('username', None)
        if other_username is None:
            raise UsernameNotProvided
        other_profile = get_profile_or_404(other_username)

        if profile.is_friends_with(other_profile):
            profile.remove_friend(other_profile)
            return Response(status=status.HTTP_204_NO_CONTENT)
        else:
            raise UsersNotFriends
