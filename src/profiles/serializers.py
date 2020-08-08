from rest_framework import serializers

from .models import Profile, Relationship, FriendRequest


class ProfileSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source='user.username')

    class Meta:
        model = Profile
        fields = ('username',)
        read_only_fields = ('username',)


class RelationshipSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = '__all__'
        read_only_fields = ('id', 'created',)
