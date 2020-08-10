from rest_framework import serializers

from .models import Profile, Relationship, FriendRequest


class DynamicModelSerializer(serializers.ModelSerializer):

    def __init__(self, *args, **kwargs):

        fields = kwargs.pop('fields', None)

        super(DynamicModelSerializer, self).__init__(*args, **kwargs)

        if fields is not None:
            allowed = set(fields)
            existing = set(self.fields.keys())
            for field_name in existing - allowed:
                self.fields.pop(field_name)


class RelationshipSerializer(serializers.ModelSerializer):

    class Meta:
        model = Relationship
        fields = ('id', 'created', 'from_profile', 'to_profile', 'status')


class FriendRequestSerializer(serializers.ModelSerializer):
    class Meta:
        model = FriendRequest
        fields = ('id', 'created', 'from_profile', 'to_profile', 'status')


class LimitedProfileSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name',
                                       read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name',)


class ProfileSerializer(DynamicModelSerializer):
    PUBLIC_FIELDS = ('username', 'first_name', 'last_name', 'friends',)
    PRIVATE_FIELDS = (PUBLIC_FIELDS +
                      ('blocking', 'incoming_requests', 'outgoing_requests',))

    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name',
                                       read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)

    # friends = LimitedProfileSerializer(many=True, read_only=True,
    #                                    source='get_friends')
    #
    # blocking = LimitedProfileSerializer(many=True, read_only=True,
    #                                     source='get_blocking')
    #
    # incoming_requests = FriendRequestSerializer(many=True, read_only=True,
    #                                             source='get_incoming_pending')
    #
    # outgoing_requests = FriendRequestSerializer(many=True, read_only=True,
    #                                             source='get_outgoing_pending')

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', 'friends',
                  'blocking', 'incoming_requests', 'outgoing_requests',)

    def update(self, instance, validated_data):
        first_name = validated_data.pop('first_name', None)
        last_name = validated_data.pop('last_name', None)
        super(ProfileSerializer, self).update(instance, validated_data)
        if first_name is not None:
            instance.user.first_name = first_name
            instance.user.save(update_fields=('first_name',))
        if last_name is not None:
            instance.user.last_name = last_name
            instance.user.save(update_fields=('last_name',))
        return instance


