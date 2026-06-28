import logging
from sqlalchemy.orm import Session

from app.infrastructure.models.auth.users import User as ORMUser
from app.domain.entities.user import User as DomainUser 
from app.domain.interfaces.user_repository import IUserRepository

logger = logging.getLogger("assistly")

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: DomainUser) -> DomainUser:
        db_user = ORMUser(
            id=user.id,
            email=user.email,
            name=user.name,
            phone=user.phone,
            avatar_url=user.avatar_url,
            bio=user.bio,
            timezone=user.timezone,
            password_hash=user.password_hash,
            is_active=user.is_active,
            is_verified=user.is_verified,
            auth_provider=user.auth_provider,
            is_system_admin=user.is_system_admin,
            last_active_tenant_slug=user.last_active_tenant_slug
        )
        
        self.db.add(db_user)
        self.db.flush()
        self.db.refresh(db_user)
        
        user.id = str(db_user.id)
        return user

    def get_by_email(self, email: str) -> DomainUser | None:
        db_user = self.db.query(ORMUser).filter(ORMUser.email == email).first()
        if not db_user:
            return None
            
        return DomainUser(
            id=str(db_user.id),
            email=db_user.email,
            name=db_user.name,
            phone=db_user.phone,
            avatar_url=db_user.avatar_url,
            bio=db_user.bio,
            timezone=db_user.timezone,
            password_hash=db_user.password_hash,
            is_active=db_user.is_active,
            is_verified=db_user.is_verified,
            auth_provider=db_user.auth_provider,
            is_system_admin=db_user.is_system_admin,
            last_active_tenant_slug=db_user.last_active_tenant_slug
        )

    def get_by_id(self, user_id: str) -> DomainUser | None:
        db_user = self.db.query(ORMUser).filter(ORMUser.id == user_id).first()
        if db_user:
           
            return DomainUser(
                id=str(db_user.id), 
                email=db_user.email, 
                name=db_user.name,
                phone=db_user.phone,
                avatar_url=db_user.avatar_url,
                bio=db_user.bio,
                timezone=db_user.timezone,
                password_hash=db_user.password_hash,
                is_active=db_user.is_active,
                is_verified=db_user.is_verified,
                auth_provider=db_user.auth_provider,
                is_system_admin=db_user.is_system_admin,
                last_active_tenant_slug=db_user.last_active_tenant_slug
            )
        return None

    def update_user(self, user: DomainUser) -> DomainUser:
        db_user = self.db.query(ORMUser).filter(ORMUser.id == user.id).first()
        if db_user:
            db_user.email = user.email
            db_user.name = user.name
            db_user.phone = user.phone
            db_user.avatar_url = user.avatar_url
            db_user.bio = user.bio
            db_user.timezone = user.timezone
            db_user.password_hash = user.password_hash
            db_user.is_active = user.is_active
            db_user.is_verified = user.is_verified
            db_user.last_active_tenant_slug = user.last_active_tenant_slug
            
            self.db.flush()
            self.db.refresh(db_user)
        return user

    def delete_user(self, user: DomainUser) -> None:
        db_user = self.db.query(ORMUser).filter(ORMUser.id == user.id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.flush()