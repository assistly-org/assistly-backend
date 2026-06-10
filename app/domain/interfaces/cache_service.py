from abc import ABC, abstractmethod

class ICacheService(ABC):
    @abstractmethod
    def set(self, key: str, ttl: int, value: str) -> None: ...
    
    @abstractmethod
    def get(self, key: str) -> str | None: ...
    
    @abstractmethod
    def delete(self, key: str) -> None: ...