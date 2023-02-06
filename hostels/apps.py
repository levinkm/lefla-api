from django.apps import AppConfig
# from .signals import Create_Virtual_Wallet


class HostelsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'hostels'

    def ready(self):
        from . import signals
