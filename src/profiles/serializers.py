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


class ProfileSerializer(DynamicModelSerializer):
    PUBLIC_FIELDS = ('username', 'first_name', 'last_name',)
    PRIVATE_FIELDS = PUBLIC_FIELDS

    username = serializers.CharField(source='get_username', read_only=True)
    first_name = serializers.CharField(source='user.first_name')
    last_name = serializers.CharField(source='user.last_name')

    def update(self, instance, validated_data):
        user = validated_data.get('user', None)
        if user is not None:
            first_name = user.pop('first_name', None)
            last_name = user.pop('last_name', None)
            if first_name is not None:
                instance.user.first_name = first_name
            if last_name is not None:
                instance.user.last_name = last_name
        instance.user.save(update_fields=('first_name', 'last_name',))
        return instance

    class Meta:
        model = Profile
        fields = ('username', 'first_name', 'last_name', )


class RequestSerializer(serializers.ModelSerializer):

    from_user = serializers.CharField(source='from_profile.get_username',
                                      read_only=True)

    to_user = serializers.CharField(source='to_profile.get_username',
                                    read_only=True)

    class Meta:
        model = FriendRequest
        fields = ('created', 'from_user', 'to_user', 'status')



