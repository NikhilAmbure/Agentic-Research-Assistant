import os

from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "Agentic_Research_Assistant.settings")
app = Celery("Agentic_Research_Assistant")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()