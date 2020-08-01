from django.urls import path
from .views import (
    ProfileDetailView,
)


app_name = 'profiles'
urlpatterns = [
    path('<int:id>/', ProfileDetailView.as_view(), name='profile-detail'),
]
