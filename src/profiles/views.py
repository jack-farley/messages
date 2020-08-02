from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import (
    DetailView
)

from .models import Profile


# Create your views here.


class ProfileDetailView(LoginRequiredMixin, DetailView):

    template_name = 'profiles/profile_detail.html'

    def get_object(self):
        profile_id = self.kwargs.get('id')
        return get_object_or_404(Profile, id=profile_id)
