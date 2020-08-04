from django.shortcuts import render, get_object_or_404, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.views import View

from django.views.generic import (
    DetailView,
    CreateView,
    FormView,
)

from .models import Profile, get_profile_or_404
from .mixins import AnonymousRequiredMixin
from .forms import FriendRequestForm


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


class MyProfileView(LoginRequiredMixin, View):
    def get(self, request):
        username = self.request.user.username
        return redirect(reverse('profiles:profile-detail', kwargs={'username': username}))

    def post(self, request):
        username = self.request.user.username
        return redirect(reverse('profiles:profile-detail', kwargs={'username': username}))


class ProfileDetailView(LoginRequiredMixin, DetailView):
    template_name = 'profiles/profile_detail.html'
    queryset = Profile.objects.all()

    def get_object(self, queryset=queryset):
        username = self.kwargs.get('username')
        user = get_object_or_404(User, username=username)
        return user.profile


class FriendsListView(LoginRequiredMixin, View):
    template_name = 'friends/friends_list.html'

    def get_current_profile(self):
        username = self.kwargs.get('username')
        return get_profile_or_404(username)

    def get_queryset(self):
        return self.get_current_profile().get_friends()

    def get(self, request, *args, **kwargs):
        context = {'current_profile': self.get_current_profile(), 'object_list': self.get_queryset()}
        return render(request, self.template_name, context)


class SendFriendRequestView(LoginRequiredMixin, FormView):
    template_name = 'friends/add_friends.html'
    form_class = FriendRequestForm

    def get_form_kwargs(self):
        kwargs = super(SendFriendRequestView, self).get_form_kwargs()
        kwargs.update({'user': self.request.user})
        return kwargs

    def get_success_url(self):
        return reverse('profiles:friends-list', kwargs={'username': self.request.user.username})

    def form_valid(self, form):
        username = form.cleaned_data['username']
        self.request.user.profile.send_request(username)
        return super().form_valid(form)
