web: uvicorn app.main:app --reload --port 8000
worker: celery -A app.infrastructure.worker.celery_app worker --loglevel=info