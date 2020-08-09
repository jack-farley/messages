from rest_framework.views import APIView
from rest_framework.response import Response

from .shortcuts import get_profile_or_404
from .serializers import ProfileSerializer
from .models import Profile


class ProfileDetailView(APIView):

    def get_object(self):
        username = self.request.query_params().get('username')
        return get_profile_or_404(username)

    def get(self):
        profile = self.get_object()
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)


class ProfileListView(APIView):

    def get(self):
        queryset = Profile.objects.all()
        serializer = ProfileSerializer(queryset, many=True)
        return Response(serializer)


class FriendsListView(APIView):

    def get(self):
        username = self.request.query_params().get('username')
        profile = get_profile_or_404(username)
        serializer = ProfileSerializer(profile.get_friends(), many=True)
        return Response(serializer.data)


