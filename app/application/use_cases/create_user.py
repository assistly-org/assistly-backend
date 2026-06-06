# Business logic — "what happens when we create a user?"
# Only knows about domain — never imports FastAPI or SQLAlchemy

from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository

class CreateUser:
    def __init__(self, repo: UserRepository):
        self.repo = repo  # injected from outside

    def execute(self, name: str, email: str) -> User:
        # Business rules go here
        # e.g: check if email already exists, validate, etc.
        user = User(id=1, name=name, email=email)
        return self.repo.save(user)  # calls interface, not real DB