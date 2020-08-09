from rest_framework import serializers

from .models import Profile, Relationship, FriendRequest


class ProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name',
                                       read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name',
                  'relationships', 'friend_requests')


class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = Relationship
        fields = ('id', 'created', 'from_profile', 'to_profile', 'status')


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'created', 'from_profile', 'to_profile', 'status')

