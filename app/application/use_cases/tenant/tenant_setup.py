import secrets
import logging
from sqlalchemy.orm import Session
from app.domain.entities.tenant import Tenant
from app.domain.entities.tenant_member import TenantMember
from app.presentation.schemas.tenant import TenantCreateRequest
from app.domain.exceptions import SubdomainTakenError

logger = logging.getLogger("assistly")

class TenantSetupService:
    def __init__(
        self, 
        db: Session, 
        tenant_repo, 
        user_repo, 
        hash_service, # ⚡ We need this to hash the Widget API Key
        task_dispatcher
    ):
        self.db = db
        self.tenant_repo = tenant_repo
        self.user_repo = user_repo
        self.hash_service = hash_service
        self.task_dispatcher = task_dispatcher

    def execute(self, current_user, data: TenantCreateRequest) -> dict:
        # --- 1. VALIDATE SUBDOMAIN ---
        if self.tenant_repo.get_by_slug(data.subdomain):
            raise SubdomainTakenError("This workspace URL is already in use.")

        try:
            # --- 2. GENERATE WIDGET API KEY ---
            # Generate a secure 32-character API key
            raw_api_key = f"ast_{secrets.token_urlsafe(32)}"
            hashed_api_key = self.hash_service.hash_password(raw_api_key)

            # --- 3. CREATE TENANT ---
            new_tenant = Tenant(
                name=data.company_name,
                slug=data.subdomain,
                website_url=str(data.website_url), # Convert HttpUrl to string
                widget_api_key_hash=hashed_api_key,
                monthly_token_usage=0, # Start at 0
                owner_id=current_user.id,
                created_by=current_user.id,
            )
            new_tenant = self.tenant_repo.create_tenant(new_tenant)
            
            # Flush to generate the new_tenant.id
            self.db.flush() 
            print(f"DEBUG: The new tenant ID is {new_tenant.id}")

            # --- 4. CREATE MEMBERSHIP (Assign 'owner' role) ---
            new_membership = TenantMember(
                user_id=current_user.id,
                tenant_id=new_tenant.id,
                role="owner",
                is_active=True
            )
            self.tenant_repo.add_member(new_membership)

            # --- 5. UPDATE USER'S ACTIVE ROUTING ---
            current_user.last_active_tenant_slug = new_tenant.slug
            self.user_repo.update_user(current_user)

            # --- 6. COMMIT EVERYTHING ---
            self.db.commit()

            # --- 7. DISPATCH CELERY TASK ---
            # Creates the isolated schema & pgvector tables in the background!
            self.task_dispatcher.dispatch_tenant_creation(new_tenant.slug)

            logger.info(f"Workspace '{new_tenant.slug}' created by {current_user.email}.")

            # ⚡ Return the RAW api key just this one time so the UI can display it
            return {
                "message": "Workspace created successfully!",
                "tenant_id": str(new_tenant.id),
                "tenant_slug": new_tenant.slug,
                "widget_api_key": raw_api_key,
                "website_url" : new_tenant.website_url
            }

        except Exception as e:
            self.db.rollback()
            logger.error(f"Workspace creation failed for {current_user.email}", exc_info=True)
            raise Exception("Failed to set up workspace. Please try again.")