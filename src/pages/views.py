from django.shortcuts import render, redirect, reverse


# Create your views here.

def home_view(request):
    user = request.user

    if user.is_authenticated:
        return redirect(user.profile.get_absolute_url())

    else:
        return redirect(reverse('login'))
