from __future__ import absolute_import
import os
from celery import Celery 
from django.conf import settings
from celery.schedules import crontab

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'cerbero.settings')


app = Celery('cerbero')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks(lambda: settings.INSTALLED_APPS)

app.conf.beat_schedule = {
    'check-http-status': {
        'task': 'config.tasks.check_http_status',
        'schedule': crontab(minute='*/5'),  # Ejecutar cada 5 minutos, ajusta según tus necesidades
    },
}

@app.task(bind=True)
def debug_task(self):
    print('Request: {0!r}'.format(self.request))




