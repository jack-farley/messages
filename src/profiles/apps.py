from django.apps import AppConfig


class ProfileConfig(AppConfig):
    name = 'profiles'

    def ready(self):
        import profiles.signals