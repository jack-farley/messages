from django.urls import path
from .views import (
    ProfileDetailView,
    MyProfileView,
    FriendsListView,
    RequestsListView,
    SendFriendRequestView,
    AcceptFriendRequestView,
)


app_name = 'profiles'
urlpatterns = [
    path('', MyProfileView.as_view(), name='my-profile'),
    path('<str:username>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('<str:username>/friends/', FriendsListView.as_view(), name='friends-list'),
    path('<str:username>/requests/', RequestsListView.as_view(), name='requests-list'),
    path('<str:username>/requests/send/', SendFriendRequestView.as_view(), name='send-request'),
    path('<str:username>/requests/accept/', AcceptFriendRequestView.as_view(), name='accept-request'),


]
