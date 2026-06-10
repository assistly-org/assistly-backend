# app/infrastructure/auth/jwt_service.py
from datetime import datetime, timedelta
from typing import Optional, Dict, Any
from jose import jwt, JWTError

SECRET_KEY = "your-super-secret-key-change-this-in-production"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

class JwtService:
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
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            return payload
        except JWTError:
            return None