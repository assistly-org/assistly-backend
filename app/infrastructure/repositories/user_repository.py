# app/infrastructure/repositories/user.py
import logging
from sqlalchemy.orm import Session
from app.infrastructure.models.auth.users import User
from app.domain.repositories.user import IUserRepository  # <-- Import the interface

logger = logging.getLogger("assistly")

class UserRepository(IUserRepository):  # <-- Inherit from the interface
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: User) -> User:
        self.db.add(user)
        self.db.flush()
        self.db.refresh(user)
        return user

    def get_by_email(self, email: str) -> User | None:
        # Replaced manual prints with your custom infrastructure logger!
        logger.info(f"Database lookup initiated for email context: '{email}'")

        user = self.db.query(User).filter(User.email == email).first()

        if user:
            logger.info(f"Database lookup success. Found user ID: {user.id}")
        else:
            logger.warning(f"Database lookup empty. No record matches email: '{email}'")

        return user

    def get_by_id(self, user_id: str) -> User | None:
        return self.db.query(User).filter(User.id == user_id).first()

    def update_user(self, user: User) -> User:
        # Use flush instead of commit if this method runs inside multi-step use cases
        self.db.flush()
        self.db.refresh(user)
        return user

    def delete_user(self, user: User) -> None:
        self.db.delete(user)
        self.db.flush()