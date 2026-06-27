"""
TerritoireSport — Dashboard local
Serveur FastAPI léger qui affiche l'état du projet en temps réel.
Tourne sur http://localhost:8765
"""

import os
import json
import subprocess
from datetime import datetime
from pathlib import Path
from fastapi import FastAPI
from fastapi.responses import HTMLResponse, JSONResponse
import uvicorn

app = FastAPI(title="TerritoireSport Dashboard", version="1.0")

# ──────────────────────────────────────────────
# Helpers
# ──────────────────────────────────────────────

def run_git(args, cwd=None):
    """Lance une commande git et retourne (ok, output)."""
    try:
        result = subprocess.run(
            ["git"] + args,
            cwd=cwd or str(Path(__file__).parent),
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0, result.stdout.strip(), result.stderr.strip()
    except Exception as e:
        return False, "", str(e)


def get_git_status(repo_path):
    """Récupère l'état git d'un repo."""
    ok, out, err = run_git(["-C", repo_path, "log", "-1", "--format=%H|%ai|%s|%an"], cwd=None)
    if not ok:
        return {"error": err or "git indisponible", "available": False}

    last_commit_hash, last_commit_date, last_commit_msg, last_author = out.split("|", 3)

    ok2, out2, _ = run_git(["-C", repo_path, "status", "--short"], cwd=None)
    modified_files = out2.split("\n") if out2 else []

    ok3, out3, _ = run_git(["-C", repo_path, "rev-parse", "--abbrev-ref", "HEAD"], cwd=None)
    branch = out3 if ok3 else "?"

    ok4, out4, _ = run_git(["-C", repo_path, "log", "--oneline", "-10"], cwd=None)
    recent_commits = out4.split("\n") if out4 else []

    return {
        "available": True,
        "branch": branch,
        "last_commit": {
            "hash": last_commit_hash[:7],
            "date": last_commit_date,
            "message": last_commit_msg,
            "author": last_author,
        },
        "modified_files": [f for f in modified_files if f],
        "recent_commits": recent_commits,
    }


def ping_api(url, timeout=3):
    """Ping une URL et retourne le status."""
    try:
        import urllib.request
        req = urllib.request.urlopen(url, timeout=timeout)
        return {"online": True, "status": req.status, "url": url}
    except Exception as e:
        return {"online": False, "error": str(e)[:100], "url": url}


# ──────────────────────────────────────────────
# Endpoints
# ──────────────────────────────────────────────

@app.get("/", response_class=HTMLResponse)
def dashboard():
    """Page dashboard principale."""
    html_path = Path(__file__).parent / "dashboard.html"
    if html_path.exists():
        return HTMLResponse(html_path.read_text(encoding="utf-8"))
    return HTMLResponse("<h1>Dashboard.html manquant</h1>")


@app.get("/api/status")
def api_status():
    """État complet du projet."""
    # Détection du repo TerritoireSport
    repo_candidates = [
        Path(__file__).parent / "TerritoireSport",
        Path(__file__).parent.parent / "TerritoireSport",
        Path(__file__).parent / "..",
    ]
    repo_path = None
    for candidate in repo_candidates:
        if (candidate / ".git").exists():
            repo_path = str(candidate.resolve())
            break

    git_data = get_git_status(repo_path) if repo_path else {"available": False, "error": "Repo non trouvé"}

    # Ping des services
    services = {
        "local_territoiresport": ping_api("http://localhost:8000/api/health"),
        "railway_prod": ping_api("https://ts-backend-production.up.railway.app/api/health", timeout=5),
        "dashboard_self": ping_api("http://localhost:8765/api/status"),
    }

    return JSONResponse({
        "timestamp": datetime.now().isoformat(),
        "repo_path": repo_path,
        "git": git_data,
        "services": services,
        "todo": [
            {"label": "Migrer les tests vers nouveaux endpoints", "status": "todo"},
            {"label": "Configurer Git LFS pour data volumineux", "status": "todo"},
            {"label": "Tunnel F7/F8 — finalisation", "status": "done"},
            {"label": "Push GitHub (commit 987741a + b1e69f9)", "status": "done"},
        ],
    })


@app.get("/api/health")
def health():
    return {"status": "ok", "service": "TerritoireSport Dashboard", "version": "1.0"}


if __name__ == "__main__":
    print("=" * 60)
    print("  TerritoireSport — Dashboard local")
    print("  URL: http://localhost:8765")
    print("  Ctrl+C pour arrêter")
    print("=" * 60)
    uvicorn.run(app, host="127.0.0.1", port=8765, log_level="warning")