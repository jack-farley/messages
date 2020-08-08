from rest_framework.views import APIView
from rest_framework.response import Response

from .shortcuts import get_profile_or_404
from .serializers import ProfileSerializer


class ProfileDetailView(APIView):

    def get_object(self, username):
        return get_profile_or_404(username)

    def get(self, request, username, format=None):
        profile = self.get_object(username)
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

# class FriendsListView(APIView):
#
#     def get(self, request, format=None):
#         friends =
