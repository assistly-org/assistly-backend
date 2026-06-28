# app/infrastructure/auth/google_auth_service.py
import os
from typing import Optional
from google.oauth2 import id_token
from google.auth.transport import requests
from app.domain.interfaces.google_auth_service import IGoogleAuthService

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

class GoogleAuthService(IGoogleAuthService):

    def verify_google_token(self, token: str) -> Optional[dict]:
        try:
            payload = id_token.verify_oauth2_token(
                token,
                requests.Request(),
                GOOGLE_CLIENT_ID
            )
            return {
                "email": payload["email"],
                "name": payload.get("name"),
                "picture": payload.get("picture"),
                "google_id": payload["sub"],
            }
        except Exception:
            return None