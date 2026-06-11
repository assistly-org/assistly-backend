from typing import Protocol

class IHashService(Protocol):
    def hash_password(slef, password: str) -> str:
        pass

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        pass
