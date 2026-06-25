"""
Routes admin — Seed et maintenance
"""
from fastapi import APIRouter, HTTPException
import os
import subprocess
from pathlib import Path

router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.post("/seed")
async def run_seed():
    """Lance le script seed.py (idempotent)."""
    try:
        result = subprocess.run(
            ["python3", "seed.py"],
            capture_output=True,
            text=True,
            timeout=30,
            cwd=os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
        )
        return {
            "success": result.returncode == 0,
            "stdout": result.stdout,
            "stderr": result.stderr,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/reset")
async def reset_db():
    """Supprime la DB et relance le seed (DANGER)."""
    try:
        db_path = os.getenv("DB_PATH", "data/territoiresport.db")
        if os.path.exists(db_path):
            os.remove(db_path)
        # Recréer le schéma
        schema_path = Path("data/schema.sql")
        if schema_path.exists():
            import sqlite3
            conn = sqlite3.connect(db_path)
            conn.executescript(schema_path.read_text())
            conn.close()
        # Relancer le seed
        result = subprocess.run(
            ["python3", "seed.py"],
            capture_output=True,
            text=True,
            timeout=30,
        )
        return {
            "success": True,
            "message": "DB reset and reseeded",
            "seed_output": result.stdout,
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/info")
async def admin_info():
    """Info système pour debug."""
    db_path = os.getenv("DB_PATH", "data/territoiresport.db")
    return {
        "db_path": db_path,
        "db_exists": os.path.exists(db_path),
        "db_size_bytes": os.path.getsize(db_path) if os.path.exists(db_path) else 0,
        "cwd": os.getcwd(),
    }