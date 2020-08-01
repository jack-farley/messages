from django.db import models
from django.contrib.auth.models import User
from django.shortcuts import reverse


# Create your models here.

class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')

    def get_absolute_url(self):
        return reverse('profiles:profile-detail', kwargs={'id': self.id})

