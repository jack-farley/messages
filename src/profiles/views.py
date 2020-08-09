from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .shortcuts import get_profile_or_404
from .serializers import ProfileSerializer
from .models import Profile



# class MyProfileView(APIView):
#
#     def get(self):



class ProfileDetailView(APIView):

    permission_classes = (IsAuthenticated, )

    def get_object(self):
        username = self.request.query_params().get('username')
        return get_profile_or_404(username)

    def get(self):
        profile = self.get_object()
        serializer = \
            ProfileSerializer(profile, fields=ProfileSerializer.PUBLIC_FIELDS)
        return Response(serializer.data)


class ProfileListView(APIView):

    permission_classes = (IsAuthenticated, )

    def get(self):
        queryset = Profile.objects.all()
        serializer = ProfileSerializer(queryset, many=True)
        return Response(serializer)


