web: uvicorn app.main:app --reload --port 8000
worker_fast: celery -A app.infrastructure.worker.celery_app worker -Q celery --concurrency=4 --loglevel=info
worker_migrations: celery -A app.infrastructure.worker.celery_app worker -Q migrations --concurrency=1 --loglevel=info