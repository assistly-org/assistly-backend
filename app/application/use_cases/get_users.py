from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository

class GetUsers:
    def __init__(self, repo: UserRepository):
        self.repo = repo

    def execute(self) -> list[User]:
        return self.repo.get_all()