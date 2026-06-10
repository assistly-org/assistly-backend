import redis
import os

redis_db = redis.Redis(
    host=os.getenv("REDIS_HOST"),
    port=os.getenv("REDIS_PORT"),
    db=os.getenv("REDIS_DB"),
    decode_responses=os.getenv("REDIS_DECODE_RESPONSES"),
)
