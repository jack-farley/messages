from django.contrib.auth import get_user_model
from django.http import Http404

from .exceptions import UsernameNotProvided


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


def get_other_profile(request):
    other_username = request.data.get('username', None)
    if other_username is None:
        raise UsernameNotProvided
    other_profile = get_profile_or_404(other_username)
    return other_profile
