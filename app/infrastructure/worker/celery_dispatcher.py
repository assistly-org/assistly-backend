from app.infrastructure.worker.email.tasks import send_otp_email_task
from app.infrastructure.worker.tenant_tasks import tenant_create_task

class CeleryTaskDispatcher:
    def dispatch_tenant_creation(self, tenant_slug: str):
        tenant_create_task.delay(tenant_slug)

    def dispatch_otp_email(self, email: str, otp_code: str):
        send_otp_email_task.delay(email, otp_code)