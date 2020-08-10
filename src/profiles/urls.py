from django.urls import path
from .views import (
    ProfileView,
)


app_name = 'profiles'
urlpatterns = [
    path('<str:username>/', ProfileView.as_view(), name='profile'),
]
