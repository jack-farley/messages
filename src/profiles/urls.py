from django.urls import path
from .views import (
    ProfileView,
    FriendsView
)


app_name = 'profiles'
urlpatterns = [
    path('<str:username>/', ProfileView.as_view(), name='profile'),
    path('<str:username>/friends/', FriendsView.as_view(), name='friends'),
    path('<str:username>/requests/', RequestsView.as_view(), name='requests'),
]
