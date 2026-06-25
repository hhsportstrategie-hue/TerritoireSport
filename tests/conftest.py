"""Configuration pytest + fixtures communes."""
import os
import sys
import pytest
import tempfile
import aiosqlite
from pathlib import Path

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Utiliser une DB temporaire pour les tests
@pytest.fixture(autouse=True)
def temp_db(monkeypatch):
    """Crée une DB temporaire pour chaque test."""
    with tempfile.NamedTemporaryFile(suffix=".db", delete=False) as f:
        db_path = f.name
    monkeypatch.setenv("DB_PATH", db_path)
    yield db_path
    os.unlink(db_path)


@pytest.fixture
async def db():
    """Crée une DB avec le schéma initialisé."""
    from main import init_db
    db_path = os.environ.get("DB_PATH", ":memory:")
    await init_db()
    yield db_path