import uuid

from django.db import models
from django.conf import settings
from django.shortcuts import reverse


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE,
        related_name='profile')

    # friends and blocked
    relationships = models.ManyToManyField(
        'self', through='Relationship', symmetrical=False,
        related_name='related_to')

    def __str__(self):
        return f'{self.user.username}'

    def get_absolute_url(self):
        return reverse('profiles:profiles-detail',
                       kwargs={'username': self.user.username})

    # GENERAL USER INFORMATION

    def get_username(self):
        return self.user.username

    # RELATIONSHIPS

    # Getting information about relationships

    def get_relationships(self, status):
        return self.relationships.filter(
            to_profile__status=status,
            to_profile__from_profile=self)

    def get_related_to(self, status):
        return self.related_to.filter(
            from_profile__status=status,
            from_profile__to_profile=self)

    def get_friends(self):
        return self.get_relationships(1)

    def get_blocking(self):
        return self.get_relationships(2)

    def is_blocked_by(self, profile):
        if self.get_related_to(2).filter(id=profile.id).exists():
            return True
        return False

    def is_blocking(self, profile):
        if self.get_relationships(2).filter(id=profile.id).exists():
            return True
        return False

    def is_friends_with(self, profile):
        friends = self.get_friends()
        if friends.filter(id=profile.id).exists():
            return True
        return False

    #

    # Creating, updating, or removing relationships relationships

    def add_relationship(self, profile, status, symmetric=True):
        if self == profile:
            return None

        relationship, created = Relationship.objects.get_or_create(
            from_profile=self,
            to_profile=profile,
            status=status
        )
        if symmetric:
            profile.add_relationship(self, status, False)
        return relationship

    def remove_relationship(self, profile, status, symmetric=True):
        Relationship.objects.filter(
            from_profile=self,
            to_profile=profile,
            status=status).delete()
        if symmetric:
            profile.remove_relationship(self, status, False)
        return

    def block(self, profile):
        if self.is_friends_with(profile):
            self.remove_relationship(profile, 1)

        if self.has_pending_request_to(profile):
            self.cancel_request(profile)

        if profile.has_pending_request_to(self):
            self.deny_request(profile)

        self.add_relationship(profile, 2, False)

    def unblock(self, profile):
        self.remove_relationship(profile, 2, False)

    def filter_blockers(self, queryset):
        for profile in queryset:
            if profile.is_blocking(self):
                queryset = queryset.objects.exclude(id=profile.id)
        return queryset

    def add_friend(self, profile):
        if not self.is_blocking(profile) \
                and not self.is_blocked_by(profile) \
                and not self.is_friends_with(profile):
            self.add_relationship(profile, 1)

    def remove_friend(self, profile):
        self.remove_relationship(profile, 1)

    #

    # FRIEND REQUESTS

    # Getting information about friend requests
    def get_incoming_requests(self, status):
        return self.incoming_requests.filter(
            status=status
        )

    def get_outgoing_requests(self, status):
        return self.outgoing_requests.filter(
            status=status
        )

    def get_incoming_pending(self):
        return self.get_incoming_requests(3)

    def get_outgoing_pending(self):
        return self.get_outgoing_requests(3)

    def has_pending_request_to(self, profile):
        outgoing_pending = self.get_outgoing_pending()
        if outgoing_pending.filter(to_profile=profile).exists():
            return True
        return False

    def has_pending_request_from(self, profile):
        incoming_pending = self.get_incoming_pending()
        if incoming_pending.filter(from_profile=profile).exists():
            return True
        return False

    # Interacting with friend requests

    def send_request(self, profile):
        if profile == self:
            return None

        if not self.is_friends_with(profile) \
                and not self.is_blocked_by(profile) \
                and not self.is_blocking(profile) \
                and not self.has_pending_request_to(profile)\
                and not self.has_pending_request_from(profile):
            request, created = FriendRequest.objects.get_or_create(
                from_profile=self,
                to_profile=profile,
                status=3,
            )
            return request

        return None

    def cancel_request(self, profile):
        request = FriendRequest.objects.filter(
            from_profile=self,
            to_profile=profile,
            status=3).first()
        if request is not None:
            request.status = 4
            request.save()
        return request

    def approve_request(self, profile):
        request = FriendRequest.objects.filter(
            from_profile=profile,
            to_profile=self,
            status=3).first()
        if request is not None:
            request.status = 1
            request.save()
            self.add_friend(profile)
        return request

    def deny_request(self, profile):
        request = FriendRequest.objects.filter(
            from_profile=profile,
            to_profile=self,
            status=3).first()
        if request is not None:
            request.status = 2
            request.save()
        return request


class Relationship(models.Model):
    RELATIONSHIP_FRIENDS = 1
    RELATIONSHIP_BLOCKED = 2
    RELATIONSHIP_STATUSES = (
        (RELATIONSHIP_FRIENDS, 'Friends'),
        (RELATIONSHIP_BLOCKED, 'Blocked'),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    from_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='from_profile')

    to_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='to_profile')

    status = models.IntegerField(choices=RELATIONSHIP_STATUSES)

    def __str__(self):
        if self.status == 1:
            return 'Friendship'
        else:
            return 'Blocking'


class FriendRequest(models.Model):
    REQUEST_ACCEPTED = 1
    REQUEST_REJECTED = 2
    REQUEST_PENDING = 3
    REQUEST_CANCELED = 4
    REQUEST_STATUSES = (
        (REQUEST_ACCEPTED, "Accepted"),
        (REQUEST_REJECTED, "Rejected"),
        (REQUEST_PENDING, "Pending"),
        (REQUEST_CANCELED, "Canceled"),
    )

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

    created = models.DateTimeField(auto_now_add=True, editable=False)

    from_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='outgoing_requests')

    to_profile = models.ForeignKey(
        Profile, on_delete=models.CASCADE, related_name='incoming_requests')

    status = models.IntegerField(choices=REQUEST_STATUSES)

    def __str__(self):
        return f'Friend request from {self.from_profile.user.username} to ' \
               f'{self.to_profile.user.username}.'
