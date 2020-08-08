from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin

from .models import User


# Register your models here.

class UserAdmin(DefaultUserAdmin):
    pass


admin.site.register(User, UserAdmin)
