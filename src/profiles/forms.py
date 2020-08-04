from django import forms
from django.contrib.auth.forms import UsernameField
from .shortcuts import get_profile


class FriendRequestForm(forms.Form):
    username = UsernameField(required=True, widget=forms.TextInput(attrs={'autofocus': True}))

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super(FriendRequestForm, self).__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data['username']
        if username is None:
            raise forms.ValidationError("Please enter a username.")

        other_profile = get_profile(username)

        if other_profile is None:
            raise forms.ValidationError("No user with that username.")

        current_profile = self.user.profile

        if current_profile.get_friends().filter(id=other_profile.id).exists():
            raise forms.ValidationError("You are already friends with that user.")

        if current_profile.has_pending_request_to(other_profile.user.username):
            raise forms.ValidationError("You already have a pending friend request with that user.")

        return username
