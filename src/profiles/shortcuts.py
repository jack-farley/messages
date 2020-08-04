from django.contrib.auth.models import User
from django.http import Http404


def get_profile(username):
    user = User.objects.filter(username=username).first()
    if user is None:
        return None
    return user.profile


def get_profile_or_404(username):
    user = User.objects.filter(username=username).first()
    if user is None:
        raise Http404("Profile does not exist.")
    return user.profile
