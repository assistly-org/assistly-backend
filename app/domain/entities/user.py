# The core User object — pure Python, no imports from FastAPI or DB
# This represents what a "User" means in your business world

class User:
    def __init__(self, id: int, name: str, email: str):
        self.id = id
        self.name = name
        self.email = email