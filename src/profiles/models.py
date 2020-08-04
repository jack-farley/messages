from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


def get_profile(profile_id):
    profile = Profile.objects.filter(id=profile_id).first()
    return profile


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    relationships = models.ManyToManyField('self', through='Relationship', symmetrical=False,
                                           related_name='related_to+')
    friend_requests = models.ManyToManyField('self', through='FriendRequest', symmetrical=False,
                                             related_name='incoming_requests')

    def get_absolute_url(self):
        return reverse('profiles:profile-detail', kwargs={'id': self.id})

    # RELATIONSHIPS

    # Getting information about relationships

    def get_relationships(self, status):
        return self.relationships.filter(to_profiles__status=status, to_profiles__from_profile=self)

    def get_related_to(self, status):
        return self.related_to.filter(from_profiles__status=status, from_profiles__to_profile=self)

    def get_friends(self):
        return self.get_relationships(1)

    def is_blocked_by(self, profile_id):
        other_profile = get_profile(id)
        if self.get_related_to(2).contains(other_profile):
            return True
        return False

    def is_blocking(self, profile_id):
        other_profile = get_profile(id)
        if self.get_relationships(2).contains(other_profile):
            return True
        return False

    def is_friends_with(self, profile_id):
        other_profile = get_profile(id)
        friends = self.get_friends()
        if friends.contains(other_profile):
            return True
        return False

    #

    # Creating, updating, or removing relationships relationships

    def add_relationship(self, user, status, symmetric=True):
        relationship, created = Relationship.objects.get_or_create(
            from_profile=self,
            to_profile=user,
            status=status
        )
        if symmetric:
            user.add_relationship(self, status, False)
        return relationship

    def remove_relationship(self, user, status, symmetric=True):
        Relationship.objects.filter(
            from_profile=self,
            to_profile=user,
            status=status).delete()
        if symmetric:
            user.remove_relationship(self, status, False)
        return

    def block(self, profile_id):
        other_profile = get_profile(profile_id)
        if self.is_friends_with(profile_id):
            self.remove_relationship(other_profile, 1)
        self.add_relationship(other_profile, 2, False)

    def unblock(self, profile_id):
        other_profile = get_profile(profile_id)
        self.remove_relationship(other_profile, 2, False)

    def add_friend(self, profile_id):
        other_profile = get_profile(profile_id)
        self.add_relationship(other_profile, 1)

    def remove_friend(self, profile_id):
        other_profile = get_profile(profile_id)
        self.remove_relationship(other_profile, 2)

    # FRIEND REQUESTS

    # Getting information about friend requests

    def get_incoming_requests(self):
        self.incoming_requests.filter(senders__status=3, senders__to_profile=self)

    def has_pending_request_to(self, profile_id):
        other_profile = get_profile(profile_id)
        if self.friend_requests.filter(receivers__status=3, receivers__from_profile=self).contains(other_profile):
            return True
        return False

    # Interacting with friend requests

    def send_request(self, profile_id):
        other_profile = get_profile(profile_id)
        if not self.get_friends().contains(other_profile) and not self.is_blocked_by(other_profile):
            request, created = FriendRequest.objects.get_or_create(
                from_profile=self,
                to_profile=other_profile,
                status=3,
            )
            return request
        return None

    def cancel_request(self, profile_id):
        other_profile = get_profile(profile_id)
        request = FriendRequest.objects.filter(from_profile=self, to_profile=other_profile, status=3).first()
        if request is not None:
            request.status = 4
        return request

    def approve_request(self, profile_id):
        other_profile = get_profile(profile_id)
        request = FriendRequest.objects.filter(from_profile=other_profile, to_profile=self, status=3).first()
        if request is not None:
            request.status = 1
            self.add_friend(profile_id)
        return request

    def deny_request(self, profile_id):
        other_profile = get_profile(profile_id)
        request = FriendRequest.objects.filter(from_profile=other_profile, to_profile=self, status=3).first()
        if request is not None:
            request.status = 2
        return request


RELATIONSHIP_FRIENDS = 1
RELATIONSHIP_BLOCKED = 2
RELATIONSHIP_STATUSES = (
    (RELATIONSHIP_FRIENDS, 'Friends'),
    (RELATIONSHIP_BLOCKED, 'Blocked'),
)


class Relationship(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    from_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='from_profiles')
    to_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='to_profiles')
    status = models.IntegerField(choices=RELATIONSHIP_STATUSES)


REQUEST_ACCEPTED = 1
REQUEST_DENIED = 2
REQUEST_PENDING = 3
REQUEST_CANCELED = 4
REQUEST_STATUSES = (
    (REQUEST_ACCEPTED, "Accepted"),
    (REQUEST_DENIED, "Denied"),
    (REQUEST_PENDING, "Pending"),
    (REQUEST_CANCELED, "Canceled"),
)


class FriendRequest(models.Model):
    created = models.DateTimeField(auto_now_add=True, editable=False)
    from_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='senders')
    to_profile = models.ForeignKey(Profile, on_delete=models.CASCADE, related_name='receivers')
    status = models.IntegerField(choices=REQUEST_STATUSES)
