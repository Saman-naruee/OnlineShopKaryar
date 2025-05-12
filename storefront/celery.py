import os
from celery import Celery
import celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "storefront.settings")

celery_app = Celery("storefront")

celery_app.config_from_object("django.conf:settings", namespace="CELERY")
celery_app.autodiscover_tasks()
