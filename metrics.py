"""
Métriques et monitoring
"""
import time
from collections import defaultdict

_metrics = defaultdict(lambda: {"count": 0, "total_time": 0, "errors": 0})

def track_request(endpoint: str, duration: float, error: bool = False):
    """Enregistre une requête."""
    m = _metrics[endpoint]
    m["count"] += 1
    m["total_time"] += duration
    if error:
        m["errors"] += 1

def get_metrics():
    """Retourne les métriques."""
    result = {}
    for endpoint, m in _metrics.items():
        count = m["count"]
        result[endpoint] = {
            "count": count,
            "avg_time_ms": round((m["total_time"] / count * 1000) if count else 0, 2),
            "errors": m["errors"],
            "error_rate": round((m["errors"] / count) if count else 0, 4)
        }
    return result
