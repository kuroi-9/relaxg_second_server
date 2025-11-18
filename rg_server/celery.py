import os
from celery import Celery

# set the default Django settings module
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rg_server.settings")

app = Celery("rg_server")

# Load task modules from all registered Django app configs.
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

@app.task(bind=True)
def debug_task(self):
    print(f"Request: {self.request!r}")
