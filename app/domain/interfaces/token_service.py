from abc import ABC, abstractmethod


class ITokenService(ABC):
    @abstractmethod
    def create_access_token(self, data: dict) -> str: ...

    @abstractmethod
    def create_refresh_token(self, data: dict) -> str: ...

    @abstractmethod
    def create_token(self, data: dict) -> str: ...

    @abstractmethod
    def decode_token(self, data: dict) -> str: ...
