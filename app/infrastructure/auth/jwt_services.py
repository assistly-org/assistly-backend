from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt
from app.domain.interfaces.token_service import ITokenService

import os

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = os.getenv("JWT_ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 30))
REFRESH_TOKEN_EXPIRE_DAYS = int(os.getenv("REFRESH_TOKEN_EXPIRE_DAYS", 7))


class JwtService(ITokenService):

    @staticmethod
    def create_token(data: dict, expires_delta: timedelta, token_type: str) -> str:
        to_encode = data.copy()
        expire = datetime.utcnow() + expires_delta

        # We explicitly tag the token type so they cannot be swapped
        to_encode.update({"exp": expire, "token_type": token_type})
        return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

    @staticmethod
    def create_access_token(data: dict) -> str:
        expires = timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
        return JwtService.create_token(data, expires, "access")

    @staticmethod
    def create_refresh_token(data: dict) -> str:
        expires = timedelta(days=REFRESH_TOKEN_EXPIRE_DAYS)
        return JwtService.create_token(data, expires, "refresh")

    @staticmethod
    def decode_token(token: str) -> Optional[Dict[str, Any]]:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
