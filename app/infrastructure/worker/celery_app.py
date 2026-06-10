import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "assistly_worker",
    broker=redis_url,
    backend=redis_url,
    # This tells Celery exactly where your background tasks are written
    include=[
        "app.infrastructure.email.tasks",
        "app.infrastructure.worker.tenant_tasks",  
    ],
)

# Recommended configuration for development tracking
celery_app.conf.update(task_track_started=True, timezone="UTC")
