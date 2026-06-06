# Abstract interface — a CONTRACT that infrastructure must follow
# domain never knows HOW data is saved, just WHAT methods exist

from abc import ABC, abstractmethod
from app.domain.entities.user import User

class UserRepository(ABC):

    @abstractmethod
    def save(self, user: User) -> User:
        pass  # infrastructure will implement this

    @abstractmethod
    def get_all(self) -> list[User]:
        pass  # infrastructure will implement this

    @abstractmethod
    def delete_user(self,id:int) -> str:
        pass