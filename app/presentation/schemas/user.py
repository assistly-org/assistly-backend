# Pydantic models — only for HTTP request/response validation
# Separate from domain entities on purpose

from pydantic import BaseModel

class UserCreateRequest(BaseModel):
    name: str
    email: str

class UserResponse(BaseModel):
    id: int
    name: str
    email: str