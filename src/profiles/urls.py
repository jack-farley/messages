from django.urls import path
from .views import (
    ProfileDetailView,
    MyProfileView,
)


app_name = 'profiles'
urlpatterns = [
    path('<int:id>/', ProfileDetailView.as_view(), name='profile-detail'),
    path('', MyProfileView.as_view(), name='my-profile'),
]
