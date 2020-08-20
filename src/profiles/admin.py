from django.contrib import admin
from django.contrib.auth.models import Group
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from django.utils.html import format_html

from .models import Profile, Relationship


def show_url(url_obj, text):
    return format_html("<a href='{url}'>{text}</a>",
                       url=reverse('admin:{}_{}_change'.format(
                           url_obj._meta.app_label,
                           url_obj._meta.model_name),
                           args=(url_obj.id,)),
                       text=text
                       )


class RelationshipInline(admin.StackedInline):
    model = Relationship
    fk_name = 'from_profile'
    extra = 0

    fields = ('show_to_profile_url',)

    def show_to_profile_url(self, obj):
        return show_url(obj.to_profile, obj.to_profile.user.username)

    show_to_profile_url.short_description = 'Profile'

    def get_readonly_fields(self, request, obj=None):
        return 'show_to_profile_url',

    def delete_model(self, request, obj):
        obj.to_profile.remove_friend(obj.from_profile)


class FriendsInline(RelationshipInline):
    verbose_name_plural = 'Friends'

    def get_queryset(self, request):
        qs = super(FriendsInline, self).get_queryset(request)
        return qs.filter(status=1)


class BlockingInline(RelationshipInline):
    verbose_name_plural = 'Blocking'

    def get_queryset(self, request):
        qs = super(BlockingInline, self).get_queryset(request)
        return qs.filter(status=2)


class ProfileAdmin(admin.ModelAdmin):
    inlines = (FriendsInline, BlockingInline)

    fieldsets = [
        ('User', {'fields': ['show_user_url_with_username', ]})
    ]
    list_display = ('show_profile_url', 'show_user_url',)

    def show_profile_url(self, obj):
        return show_url(obj, obj.user.username)

    def show_user_url(self, obj):
        return show_url(obj.user, 'User')

    def show_user_url_with_username(self, obj):
        return show_url(obj.user, obj.user.username)

    show_profile_url.short_description = "Username"
    show_user_url.short_description = "User URL"
    show_user_url_with_username.short_description = "User"

    def get_readonly_fields(self, request, obj=None):
        return ['user', 'show_user_url_with_username', ]

    def has_add_permission(self, request, obj=None):
        return False

    def delete_queryset(self, request, queryset):
        for obj in queryset:
            obj.user.delete()

    def delete_model(self, request, obj):
        obj.user.delete()


class CustomUserAdmin(UserAdmin):
    fieldsets = UserAdmin.fieldsets + (
        ('Profile', {'fields': ['show_profile_url', ]}),
    )

    def show_profile_url(self, obj):
        return show_url(obj.profile, obj.username)

    show_profile_url.short_description = "Profile"

    def get_readonly_fields(self, request, obj=None):
        return super(CustomUserAdmin, self).get_readonly_fields(request, obj) \
               + ('show_profile_url',)


# Register your models here.
admin.site.unregister(get_user_model())
admin.site.register(get_user_model(), CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin, )
admin.site.unregister(Group)
