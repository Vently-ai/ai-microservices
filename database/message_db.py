import redis
from config import Config

_redis_client = None

def get_client():
    global _redis_client
    if _redis_client is None:
        _redis_client = redis.Redis(
            **Config.REDIS,
            decode_responses=True, # returns strings instead of bytes
        )
    return _redis_client

def format_key(session_id: str) -> str:
    return f"session:{session_id}"