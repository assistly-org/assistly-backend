# infrastructure/cache/redis_service.py
from app.domain.interfaces.cache_service import ICacheService
from app.infrastructure.cache.redis_client import redis_db

class RedisService(ICacheService):
    def set(self, key: str, ttl: int, value: str) -> None:
        redis_db.setex(key, ttl, value)

    def get(self, key: str) -> str | None:
        return redis_db.get(key)

    def delete(self, key: str) -> None:
        redis_db.delete(key)