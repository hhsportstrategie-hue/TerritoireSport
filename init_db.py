"""
Initialise la base de données avec toutes les tables nécessaires.
Source unique de vérité : data/schema.sql
"""
import sqlite3
import os
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "territoiresport.db"))


def init_db():
    """Applique data/schema.sql (source unique de vérité).

    Note: NE SUPPRIME PLUS la DB existante. Le schéma SQL utilise
    CREATE TABLE IF NOT EXISTS, donc il complète la DB sans perte de données.
    """
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    schema_path = Path(__file__).parent / "data" / "schema.sql"
    if not schema_path.exists():
        raise FileNotFoundError(f"Schéma SQL introuvable: {schema_path}")

    conn = sqlite3.connect(DB_PATH)
    conn.executescript(schema_path.read_text())
    conn.commit()
    conn.close()
    print(f"✅ Schéma appliqué: {schema_path}")


if __name__ == "__main__":
    init_db()
