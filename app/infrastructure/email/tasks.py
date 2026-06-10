# app/infrastructure/email/tasks.py
from app.infrastructure.worker.celery_app import  celery_app
from app.infrastructure.email.smtp_services import EmailService

@celery_app.task(name="send_otp_email_task")

def send_otp_email_task(to_email: str, otp_code: str):
    """
    This function is executed entirely by the Celery worker process, 
    leaving your FastAPI application free to handle incoming web traffic.
    """
    try:
        email_service = EmailService()
        email_service.send_otp(to_email=to_email, otp_code=otp_code)
        return f"Successfully processed OTP delivery to {to_email}"
    except Exception as e:
        print(f"CRITICAL: Celery task execution failed: {e}")
        return f"Failed delivery to {to_email}"
    
    
# @celery_app.tasks(name="tenant_create")