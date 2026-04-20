from django.apps import AppConfig
import sys, os

class ApiConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'api'

    def ready(self):
        # чтобы не дублировалось при autoreload
        if 'runserver' in sys.argv and os.environ.get('RUN_MAIN') != 'true':
            return
        from .jobs import start
        start()
        from . import signals  # noqa
        from . import utils  # noqa