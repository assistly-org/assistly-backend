# app/domain/interfaces/google_auth_service.py
from abc import ABC, abstractmethod
from typing import Optional

class IGoogleAuthService(ABC):
    
    @abstractmethod
    def verify_google_token(self, id_token: str) -> Optional[dict]:
        """
        Verifies the Google ID token and returns the payload.
        Returns None if token is invalid.
        """
        pass