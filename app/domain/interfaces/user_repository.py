# app/domain/repositories/user.py
from abc import ABC, abstractmethod
from typing import Optional
# from app.infrastructure.models.auth.users import User
from app.domain.entities.user import User

class IUserRepository(ABC):

    @abstractmethod
    def create_user(self, user: User) -> User:
        """Stages a new user record into data store memory."""
        pass

    @abstractmethod
    def get_by_email(self, email: str) -> Optional[User]:
        """Retrieves a user by their unique email address."""
        pass

    @abstractmethod
    def get_by_id(self, user_id: str) -> Optional[User]:
        """Retrieves a user by their unique primary key ID."""
        pass

    @abstractmethod
    def update_user(self, user: User) -> User:
        """Updates an existing user's state in the data store."""
        pass

    @abstractmethod
    def delete_user(self, user: User) -> None:
        """Removes a user record permanently from the data store."""
        pass