from django.contrib.auth import get_user_model
from django.http import Http404


def get_profile(username):
    user = get_user_model().objects.filter(username=username).first()
    if user is None:
        return None
    return user.profile


def get_profile_or_404(username):
    user = get_user_model().objects.filter(username=username).first()
    if user is None:
        raise Http404("Profile does not exist.")
    return user.profile
