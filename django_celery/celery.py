import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_video_converter.settings')

app = Celery('django_video_converter')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()