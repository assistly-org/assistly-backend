import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

celery_app = Celery(
    "assistly_worker",
    broker=redis_url,
    backend=redis_url,
    # This tells Celery exactly where your background tasks are written
    include=[
        "app.infrastructure.worker.email.tasks",
        "app.infrastructure.worker.tenant_tasks",  
        "app.infrastructure.worker.tenant_migration_tasks",  
    ],
)

celery_app.conf.update(
    task_track_started=True, 
    timezone="UTC",
    
    # ⚡ PRODUCTION GUARDRAIL: Route tasks to specific queues automatically
    task_routes={
        # Keep heavy migrations in a completely isolated 'migrations' queue
        'tasks.migrate_single_tenant_schema': {'queue': 'migrations'},
        
        # Keep everything else (like OTP emails) in the default 'celery' queue
        # Celery does this by default for unlisted tasks, but it's good to be aware!
    },
    
    # Optional but highly recommended for heavy DB tasks: 
    # Stops the worker from hoarding tasks in memory before it's ready to execute them
    worker_prefetch_multiplier=1 
)