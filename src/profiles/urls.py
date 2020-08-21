from django.urls import path
from .views import (
    ProfileView,
    FriendsView,
    RequestsView,
    BlockingView,
)


app_name = 'profiles'
urlpatterns = [
    path('<str:username>/', ProfileView.as_view(), name='profile'),
    path('<str:username>/friends/', FriendsView.as_view(), name='friends'),
    path('<str:username>/requests/', RequestsView.as_view(), name='requests'),
    path('<str:username>/blocking/', BlockingView.as_view(), name='blocks'),
]
