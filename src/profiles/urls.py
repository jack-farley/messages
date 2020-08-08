from django.urls import path
from .views import (
    ProfileDetailView,
)


app_name = 'profiles'
urlpatterns = [
    path('<str:username>/', ProfileDetailView.as_view(), name='profile-detail')
]
