"""
TerritoireSport — Dashboard local (v2)
Serveur FastAPI léger qui affiche l'état du projet en temps réel.
Tourne sur http://localhost:8765

V2 : ne dépend plus du repo Git local.
     Lit l'état du repo via l'API GitHub (pas besoin de clone local).
"""

import os
import json
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

app = FastAPI(title="TerritoireSport Dashboard", version="2.0")

# ──────────────────────────────────────────────
# Config
# ──────────────────────────────────────────────

GITHUB_REPO = "hhsportstrategie-hue/TerritoireSport"
GITHUB_API_BASE = "https://api.github.com"

SERVICES = {
    "railway_prod": {
        "url": "https://ts-backend-production.up.railway.app/api/health",
        "label": "Railway prod (backend)",
        "timeout": 5,
    },
    "local_territoiresport": {
        "url": "http://localhost:8000/api/health",
        "label": "Local TerritoireSport API",
        "timeout": 2,
    },
}

TODO = [
    {"label": "Migrer les tests vers nouveaux endpoints", "status": "todo"},
    {"label": "Configurer Git LFS pour data volumineux", "status": "todo"},
    {"label": "Tunnel F7/F8 — finalisation", "status": "done"},
    {"label": "Push GitHub (commit 987741a + b1e69f9)", "status": "done"},
]

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def fetch_github(path):
    """GET sur l'API GitHub. Retourne (ok, data_or_error)."""
    try:
        import urllib.request
        url = f"{GITHUB_API_BASE}{path}"
        req = urllib.request.Request(
            url,
            headers={"Accept": "application/vnd.github+json", "User-Agent": "cathy-dashboard"}
        )
        with urllib.request.urlopen(req, timeout=5) as r:
            return True, json.loads(r.read().decode("utf-8"))
    except Exception as e:
        return False, str(e)[:200]


def ping_api(url, timeout=3):
    """Ping une URL et retourne un dict d'état."""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return {"online": True, "status": r.status, "url": url}
    except Exception as e:
        return {"online": False, "error": str(e)[:120], "url": url}


def get_repo_state():
    """Lit l'état du repo via l'API GitHub (pas besoin de clone local)."""
    ok, commits = fetch_github(f"/repos/{GITHUB_REPO}/commits?per_page=10")
    if not ok:
        return {"available": False, "error": commits}

    recent = []
    for c in commits:
        recent.append({
            "hash": (c.get("sha") or "")[:7],
            "message": (c.get("commit", {}).get("message") or "").split("\n")[0],
            "author": (c.get("commit", {}).get("author") or {}).get("name", ""),
            "date": (c.get("commit", {}).get("author") or {}).get("date", ""),
        })

    ok2, repo = fetch_github(f"/repos/{GITHUB_REPO}")
    branch = repo.get("default_branch", "main") if ok2 else "main"

    return {
        "available": True,
        "branch": branch,
        "last_commit": recent[0] if recent else None,
        "recent_commits": recent,
    }


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def dashboard():
    html_path = Path(__file__).parent / "dashboard.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>dashboard.html manquant à côté du serveur</h1>")


@app.get("/api/status")
def api_status():
    services = {}
    for key, cfg in SERVICES.items():
        result = ping_api(cfg["url"], timeout=cfg["timeout"])
        result["label"] = cfg["label"]
        services[key] = result

    # Le dashboard lui-même : on renvoie juste "ok" sans se re-pinger
    services["dashboard_self"] = {
        "online": True,
        "status": 200,
        "url": "http://localhost:8765/api/status",
        "label": "Dashboard (ce serveur)",
    }

    git_state = get_repo_state()

    return JSONResponse({
        "timestamp": datetime.now().isoformat(),
        "github_repo": GITHUB_REPO,
        "git": git_state,
        "services": services,
        "todo": TODO,
    })


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "TerritoireSport Dashboard", "version": "2.0"}


if __name__ == "__main__":
    print("=" * 60)
    print("  TerritoireSport — Dashboard local (v2)")
    print("  URL: http://localhost:8765")
    print("  Ctrl+C pour arrêter")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")
