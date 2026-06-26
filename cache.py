"""
Cache simple en mémoire avec TTL
"""
import time
from functools import wraps

_cache = {}

def cached(ttl_seconds=300):
    """Décorateur de cache avec TTL."""
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            key = f"{func.__name__}:{str(args)}:{str(kwargs)}"
            now = time.time()
            if key in _cache:
                value, timestamp = _cache[key]
                if now - timestamp < ttl_seconds:
                    return value
            result = await func(*args, **kwargs)
            _cache[key] = (result, now)
            return result
        return wrapper
    return decorator

def clear_cache():
    """Vide le cache."""
    _cache.clear()
