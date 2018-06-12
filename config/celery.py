import os
from celery import Celery


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.config.local')

app = Celery('app')

app.config_from_object('django.conf:settings')

app.autodiscover_tasks(related_name='tasks')
