import logging
from sqlalchemy.orm import Session

# ⚡ 1. ALIAS YOUR IMPORTS SO THEY DON'T COLLIDE
from app.infrastructure.models.auth.users import User as ORMUser
from app.domain.entities.user import User as DomainUser  # Assuming this is your path!
from app.domain.interfaces.user_repository import IUserRepository

logger = logging.getLogger("assistly")

class UserRepository(IUserRepository):
    def __init__(self, db: Session):
        self.db = db

    # ⚡ 2. Accept a DomainUser, return a DomainUser
    def create_user(self, user: DomainUser) -> DomainUser:
        
        # ⚡ 3. Map the Domain data into the SQLAlchemy ORM model
        db_user = ORMUser(
            id=user.id,
            email=user.email,
            password_hash=user.password_hash,
            # Add any other fields you have on your user model here (e.g., is_active=user.is_active)
        )
        
        # ⚡ 4. Save the ORM model to the database
        self.db.add(db_user)
        self.db.flush()
        self.db.refresh(db_user)
        
        # ⚡ 5. CRITICAL FIX: Map the DB-generated ID back to the domain object!
        # This ensures new_user.id is not 'None' when you pass it to the Tenant.
        user.id = str(db_user.id)
        
        return user

    def get_by_email(self, email: str) -> DomainUser | None:
        logger.info(f"Database lookup initiated for email context: '{email}'")
        
        db_user = self.db.query(ORMUser).filter(ORMUser.email == email).first()
        
        if db_user:
            logger.info(f"Database lookup success. Found user ID: {db_user.id}")
            # Map back to DomainUser before returning to the use case!
            return DomainUser(
                id=str(db_user.id), 
                email=db_user.email, 
                password_hash=db_user.password_hash
            )
        else:
            logger.warning(f"Database lookup empty. No record matches email: '{email}'")
            return None

    def get_by_id(self, user_id: str) -> DomainUser | None:
        db_user = self.db.query(ORMUser).filter(ORMUser.id == user_id).first()
        if db_user:
            return DomainUser(
                id=str(db_user.id), 
                email=db_user.email, 
                password_hash=db_user.password_hash
            )
        return None

    def update_user(self, user: DomainUser) -> DomainUser:
        # Fetch the existing ORM model
        db_user = self.db.query(ORMUser).filter(ORMUser.id == user.id).first()
        if db_user:
            # Update the ORM model with the new Domain data
            db_user.email = user.email
            db_user.password_hash = user.password_hash
            self.db.flush()
            self.db.refresh(db_user)
        return user

    def delete_user(self, user: DomainUser) -> None:
        db_user = self.db.query(ORMUser).filter(ORMUser.id == user.id).first()
        if db_user:
            self.db.delete(db_user)
            self.db.flush()