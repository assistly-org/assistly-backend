
from app.domain.entities.user import User
from app.domain.repositories.user_repository import UserRepository


class DeleteUser:
    def __init__(self,repo=UserRepository):
        self.repo = UserRepository

