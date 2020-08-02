from django.shortcuts import render, redirect, reverse
from django.contrib.auth.decorators import login_required


# Create your views here.

@login_required
def home_view(request):
    user = request.user

    if user.is_authenticated:
        return redirect(user.profile.get_absolute_url())

    else:
        return redirect(reverse('login'))
