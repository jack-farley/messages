from django.urls import path

from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    SignUpView,
    LoginView,
)


app_name = 'accounts'
urlpatterns = [
    path('signup/', SignUpView.as_view(), name='sign-up'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token-refresh'),
]
