from django.urls import path
from .views import (
    ProfileDetailView,
    MyProfileView,
    FriendsListView,
    SendFriendRequestView,
)


app_name = 'profiles'
urlpatterns = [
    path('', MyProfileView.as_view(), name='my-profile'),
    path('<str:username>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('<str:username>/friends/', FriendsListView.as_view(), name='friends-list'),
    path('<str:username>/request/', SendFriendRequestView.as_view(), name='friend-request'),
]
