from django.apps import AppConfig


class MyAppConfig(AppConfig):
    name = 'backend_app'

# nv:12aug2018 override 'ready' to enable signals
    def ready(self):
        # from . import signals
        from .services import signals