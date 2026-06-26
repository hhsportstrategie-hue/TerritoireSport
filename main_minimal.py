"""
Version minimaliste de TerritoireSport — juste FastAPI + 2 endpoints.
Aucun lifespan, aucun subprocess, aucun StaticFiles.
Pour diagnostiquer le crash Railway.
"""
import os
from fastapi import FastAPI

app = FastAPI(title="TerritoireSport Minimal")

@app.get("/")
async def root():
    return {"status": "ok", "version": "minimal"}

@app.get("/api/health")
async def health():
    return {"status": "healthy", "db_path": os.getenv("DB_PATH", "data/territoiresport.db")}

@app.get("/api/ping")
async def ping():
    return {"pong": True}