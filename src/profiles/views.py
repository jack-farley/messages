from django.shortcuts import render, redirect, reverse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login, authenticate
from django.views import View

from django.views.generic import (
    DetailView,
    CreateView,
    FormView,
)

from .models import Profile
from .mixins import AnonymousRequiredMixin
from .shortcuts import get_profile_or_404


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
        return redirect(self.get_success_url())


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
        return get_profile_or_404(username)

    def get_context_data(self, *args, **kwargs):
        context = super(ProfileDetailView, self).get_context_data(**kwargs)
        context['is_user'] = (self.request.user == self.get_object().user)
        context['friends_with_user'] = self.request.user.profile.is_friends_with(self.get_object())
        context['pending_request_from_user'] = self.request.user.profile.has_pending_request_to(self.get_object())
        return context


class FriendsListView(LoginRequiredMixin, View):
    template_name = 'friends/friends_list.html'

    def get_current_profile(self):
        return self.request.user.profile

    def get_queryset(self):
        return self.get_current_profile().get_friends()

    def get(self, request, *args, **kwargs):
        context = {'object_list': self.get_queryset()}
        return render(request, self.template_name, context)


class SendFriendRequestView(LoginRequiredMixin, View):

    def post(self, request, username):
        profile = self.request.user.profile
        other_profile = get_profile_or_404(username)

        # check if there is already a pending request
        profile.send_request(other_profile)

        next_url = self.request.POST.get('next', '')
        if next_url is None:
            return redirect(reverse('profiles:profile-detail', kwargs={'username': username}))
        return redirect(next_url)


class RequestsListView(LoginRequiredMixin, View):
    template_name = 'friends/requests_list.html'

    def get_queryset(self):
        return self.request.user.profile.get_incoming_pending()

    def get(self, request, *args, **kwargs):
        if self.kwargs.get('username') != self.request.user.username:
            redirect(reverse('profiles:incoming-requests', kwargs={'username': self.request.user.username}))
        context = {'object_list': self.get_queryset()}
        return render(request, self.template_name, context)


class AcceptFriendRequestView(LoginRequiredMixin, View):

    def post(self, request, username):
        profile = self.request.user.profile
        other_profile = get_profile_or_404(username)

        if profile.has_pending_request_from(other_profile):
            profile.approve_request(other_profile)

        next_url = self.request.POST.get('next', '')
        if next_url is None:
            return redirect(reverse('profiles:friends-list', kwargs={'username': self.request.user.username}))
        return redirect(next_url)

# class FindProfile(LoginRequiredMixin, FormView):
#     template_name = 'profiles/find_profiles.html'
