default_app_config = 'backend_app.apps.MyAppConfig'

# This will make sure the app is always imported when
# Django starts so that shared_task will use this app.
from .my_celery import app as celery_app

__all__ = ('celery_app',)