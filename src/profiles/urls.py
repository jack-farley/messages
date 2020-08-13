from django.urls import path
from .views import (
    ProfileView,
    FriendsView
)


app_name = 'profiles'
urlpatterns = [
    path('<str:username>/', ProfileView.as_view(), name='profile'),
    path('<str:username>/', FriendsView.as_view(), name='friends'),
]
