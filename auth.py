"""
Authentification par token API — version étendue.

Tokens supportés :
- Token principal (env API_TOKEN) : admin, accès illimité
- Tokens partenaires (DB table api_tokens) : accès limité, quota journalier

Usage :
    Authorization: Bearer <token>
    ou
    X-API-Key: <token>
"""
import os
import sqlite3
import hashlib
import secrets
from datetime import datetime, timedelta
from pathlib import Path
from fastapi import HTTPException, Depends, Header
from db_config import DB_PATH

API_TOKEN = os.getenv("API_TOKEN", "territoire-sport-demo-2026")
QUOTA_PER_DAY = int(os.getenv("QUOTA_PER_DAY", "1000"))


def hash_token(token: str) -> str:
    """Hash SHA-256 du token pour stockage sécurisé."""
    return hashlib.sha256(token.encode()).hexdigest()


def _init_tokens_table():
    """Crée la table api_tokens si elle n'existe pas."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS api_tokens (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_hash TEXT UNIQUE NOT NULL,
                client_name TEXT NOT NULL,
                client_email TEXT,
                created_at TEXT NOT NULL,
                last_used_at TEXT,
                request_count INTEGER DEFAULT 0,
                quota_per_day INTEGER DEFAULT 1000,
                is_active INTEGER DEFAULT 1,
                notes TEXT
            );
            CREATE INDEX IF NOT EXISTS idx_tokens_hash ON api_tokens(token_hash);
        """)
        conn.commit()
    finally:
        conn.close()


def _verify_db_token(token: str) -> dict:
    """Vérifie un token en DB et incrémente son compteur. Retourne les infos client."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        cur = conn.cursor()
        cur.execute(
            "SELECT * FROM api_tokens WHERE token_hash = ? AND is_active = 1",
            (hash_token(token),)
        )
        row = cur.fetchone()
        if not row:
            return None

        # Vérifier quota journalier
        today = datetime.now().strftime("%Y-%m-%d")
        cur.execute(
            "SELECT COUNT(*) FROM api_token_usage WHERE token_hash = ? AND used_at LIKE ?",
            (hash_token(token), f"{today}%")
        )
        usage_today = cur.fetchone()[0]

        if usage_today >= row["quota_per_day"]:
            return {"error": "quota_exceeded", "quota": row["quota_per_day"], "used": usage_today}

        # Enregistrer usage et update last_used
        cur.execute(
            "INSERT INTO api_token_usage (token_hash, used_at) VALUES (?, ?)",
            (hash_token(token), datetime.now().isoformat())
        )
        cur.execute(
            "UPDATE api_tokens SET last_used_at = ?, request_count = request_count + 1 WHERE token_hash = ?",
            (datetime.now().isoformat(), hash_token(token))
        )
        conn.commit()

        return {
            "type": "partner",
            "client_name": row["client_name"],
            "client_email": row["client_email"],
            "quota_per_day": row["quota_per_day"],
            "used_today": usage_today + 1,
            "request_count": row["request_count"] + 1,
            "created_at": row["created_at"]
        }
    finally:
        conn.close()


async def verify_token(
    authorization: str = Header(None),
    x_api_key: str = Header(None)
):
    """
    Vérifie le token API. Accepte :
    - Header Authorization: Bearer <token>
    - Header X-API-Key: <token>
    """
    # Extraire le token des headers
    token = None
    if authorization and authorization.lower().startswith("bearer "):
        token = authorization[7:].strip()
    elif x_api_key:
        token = x_api_key.strip()

    if not token:
        raise HTTPException(
            status_code=401,
            detail="Token API manquant. Headers acceptés: Authorization: Bearer <token> ou X-API-Key: <token>"
        )

    # 1. Token principal (admin)
    if token == API_TOKEN:
        return {
            "type": "admin",
            "client_name": "admin",
            "quota_per_day": "illimité",
            "used_today": 0,
        }

    # 2. Token partenaire en DB
    result = _verify_db_token(token)
    if result:
        if "error" in result and result["error"] == "quota_exceeded":
            raise HTTPException(
                status_code=429,
                detail=f"Quota journalier dépassé ({result['used']}/{result['quota']}). Réessayez demain."
            )
        return result

    raise HTTPException(status_code=401, detail="Token API invalide")


def generate_partner_token(client_name: str, client_email: str = None, quota: int = 1000) -> str:
    """Génère un nouveau token partenaire. Retourne le token en clair (à transmettre 1 seule fois)."""
    token = secrets.token_urlsafe(32)
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.execute(
            """INSERT INTO api_tokens (token_hash, client_name, client_email, created_at, quota_per_day, is_active)
               VALUES (?, ?, ?, ?, ?, 1)""",
            (hash_token(token), client_name, client_email, datetime.now().isoformat(), quota)
        )
        conn.commit()
    finally:
        conn.close()
    return token


def init_usage_table():
    """Crée la table de log d'usage si manquante."""
    conn = sqlite3.connect(DB_PATH)
    try:
        conn.executescript("""
            CREATE TABLE IF NOT EXISTS api_token_usage (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                token_hash TEXT NOT NULL,
                used_at TEXT NOT NULL
            );
            CREATE INDEX IF NOT EXISTS idx_usage_token ON api_token_usage(token_hash);
            CREATE INDEX IF NOT EXISTS idx_usage_date ON api_token_usage(used_at);
        """)
        conn.commit()
    finally:
        conn.close()


# init_usage_table() called from main lifespan
