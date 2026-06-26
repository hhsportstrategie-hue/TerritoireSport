"""
Rate limiting simple en mémoire
"""
import time
from collections import defaultdict

_requests = defaultdict(list)

RATE_LIMIT_PER_MINUTE = 60

def check_rate_limit(client_ip: str = "default"):
    """Vérifie le rate limit. Retourne True si OK, False si dépassé."""
    now = time.time()
    minute_ago = now - 60
    _requests[client_ip] = [t for t in _requests[client_ip] if t > minute_ago]
    if len(_requests[client_ip]) >= RATE_LIMIT_PER_MINUTE:
        return False
    _requests[client_ip].append(now)
    return True
