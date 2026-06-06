# FastAPI routes — the outermost layer
# Wires everything together using Dependency Injection

from fastapi import APIRouter
from app.application.use_cases.create_user import CreateUser
from app.application.use_cases.get_users import GetUsers
from app.infrastructure.repositories.memory_user_repository import MemoryUserRepository
from app.presentation.schemas.user import UserCreateRequest, UserResponse

router = APIRouter()

# Shared repo instance (in real apps, use FastAPI Depends() properly)
repo = MemoryUserRepository()

@router.post("/users", response_model=UserResponse)
def create_user(data: UserCreateRequest):
    use_case = CreateUser(repo=repo)         # inject repo into use case
    result = use_case.execute(data.name, data.email)
    return UserResponse(id=result.id, name=result.name, email=result.email)

@router.get("/users", response_model=list[UserResponse])
def get_users():
    use_case = GetUsers(repo=repo)           # inject same repo
    users = use_case.execute()
    return [UserResponse(id=u.id, name=u.name, email=u.email) for u in users]