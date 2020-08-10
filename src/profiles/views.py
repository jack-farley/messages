from django.http import HttpResponseRedirect
from django.shortcuts import reverse

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from .shortcuts import get_profile_or_404
from .serializers import ProfileSerializer


class MyProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self):
        username = self.request.user.username
        return HttpResponseRedirect(reverse('profiles:profile',
                                            kwargs={'username': username}))


class ProfileView(APIView):
    permission_classes = (IsAuthenticated,)

    def get_object(self, username):
        return get_profile_or_404(username)

    def get(self, request, username, format=None):
        profile = self.get_object(username)

        if self.request.user.profile == profile:
            fields = ProfileSerializer.PRIVATE_FIELDS
        else:
            fields = ProfileSerializer.PUBLIC_FIELDS

        serializer = ProfileSerializer(profile, fields=fields)
        return Response(serializer.data)

    def put(self, request, username, format=None):
        profile = self.get_object(username)
        serializer = ProfileSerializer(profile, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
