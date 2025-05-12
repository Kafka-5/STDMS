import os
import django
from celery import Celery
import logging

logger = logging.getLogger(__name__)

# Set the default Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stdms.settings')

# Initialize Django
django.setup()

app = Celery('stdms')

# Load Celery settings from Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# Auto-discover tasks
app.autodiscover_tasks()

# Windows-compatible settings
app.conf.update(
    task_ignore_result=True,
    task_track_started=True,
    worker_pool='solo',
)

@app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')