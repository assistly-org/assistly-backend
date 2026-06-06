# Concrete implementation of the interface
# This is where ACTUAL saving happens (memory, DB, file, etc.)

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository

class MemoryUserRepository(UserRepository):
    def __init__(self):
        self.users: list[User] = []  # in-memory storage
        self._next_id = 1

    def save(self, user: User) -> User:
        user.id = self._next_id
        self._next_id += 1
        self.users.append(user)
        return user

    def get_all(self) -> list[User]:
        return self.users