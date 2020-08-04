from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.http import HttpResponseRedirect
from django.views import View

from django.views.generic import (
    DetailView,
    CreateView
)

from .models import Profile
from .mixins import AnonymousRequiredMixin


# Create your views here.


class UserCreateView(AnonymousRequiredMixin, CreateView):
    template_name = 'profiles/user_create.html'
    form_class = UserCreationForm

    def get_success_url(self):
        return reverse('profiles:my-profile')

    def form_valid(self, form):
        form.save()
        new_user = authenticate(username=form.cleaned_data['username'],
                                password=form.cleaned_data['password1'])
        login(self.request, new_user)
        return HttpResponseRedirect(self.get_success_url())


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'profiles/profile_detail.html'
    queryset = Profile.objects.all()

    def get_object(self, queryset=queryset):
        profile_id = self.kwargs.get('id')
        return get_object_or_404(Profile, id=profile_id)


class MyProfileView(LoginRequiredMixin, View):
    def get(self, request):
        profile_id = self.request.user.profile.id
        return redirect(reverse('profiles:profile-detail', kwargs={'id': profile_id}))

    def post(self, request):
        profile_id = self.request.user.profile.id
        return redirect(reverse('profiles:profile-detail', kwargs={'id': profile_id}))
