from django.contrib.auth import get_user_model
from django.http import Http404
from django.core.exceptions import PermissionDenied

from .exceptions import UsernameNotProvided

MESSAGE_404 = "Profile does not exist."


def get_profile(username):
    user = get_user_model().objects.filter(username=username).first()
    if user is None:
        return None
    return user.profile


def get_profile_or_404(username):
    user = get_profile(username)
    if user is None:
        raise Http404(MESSAGE_404)
    return user.profile


def check_my_profile(username, auth_profile):
    my_profile = get_profile_or_404(username)

    if auth_profile != my_profile:
        raise PermissionDenied

    return my_profile


def get_other_profile(authenticated_profile, other_username):
    # find requested profile
    if other_username is None:
        raise UsernameNotProvided
    requested_profile = get_profile_or_404(other_username)

    # check blocking
    if requested_profile.is_blocking(authenticated_profile):
        raise Http404(MESSAGE_404)

    return requested_profile
