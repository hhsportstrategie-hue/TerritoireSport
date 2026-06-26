"""
Authentification simple par token API
"""
import os
from fastapi import HTTPException, Depends, Header

API_TOKEN = os.getenv("API_TOKEN", "territoire-sport-demo-2026")

async def verify_token(x_api_key: str = Header(None)):
    """Vérifie le token API dans le header X-API-Key."""
    if x_api_key != API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Token API invalide ou manquant. Header requis: X-API-Key"
        )
    return x_api_key
