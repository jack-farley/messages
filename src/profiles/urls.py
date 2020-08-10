from django.urls import path
from .views import (
    MyProfileView,
    ProfileView,
)


app_name = 'profiles'
urlpatterns = [
    path('', MyProfileView.as_view(), name='my-profile'),
    path('<str:username>/', ProfileView.as_view(), name='profile'),

]
