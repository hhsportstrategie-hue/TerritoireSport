"""
Initialise la base de données avec toutes les tables nécessaires.
"""
import sqlite3
import os

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "territoiresport.db"))

def init_db():
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    # Supprimer la DB existante pour garantir un schéma propre
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        print(f"🗑️  Ancienne DB supprimée: {DB_PATH}")
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    
    # Table clubs
    cur.execute("""
        CREATE TABLE IF NOT EXISTS clubs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            sport TEXT,
            city TEXT,
            department TEXT,
            size TEXT,
            contact_email TEXT,
            contact_phone TEXT,
            password_hash TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Table projects
    cur.execute("""
        CREATE TABLE IF NOT EXISTS projects (
            id TEXT PRIMARY KEY,
            club_id TEXT,
            title TEXT NOT NULL,
            description TEXT,
            themes TEXT,
            budget REAL,
            status TEXT DEFAULT 'draft',
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (club_id) REFERENCES clubs(id)
        )
    """)
    
    # Table partners
    cur.execute("""
        CREATE TABLE IF NOT EXISTS partners (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            type TEXT,
            city TEXT,
            department TEXT,
            themes TEXT,
            contact_email TEXT,
            contact_url TEXT,
            description TEXT,
            created_at TEXT DEFAULT (datetime('now'))
        )
    """)
    
    # Table communes
    cur.execute("""
        CREATE TABLE IF NOT EXISTS communes (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            code_insee TEXT,
            department TEXT,
            population INTEGER,
            latitude REAL,
            longitude REAL,
            epci TEXT
        )
    """)
    
    # Table shortlists
    cur.execute("""
        CREATE TABLE IF NOT EXISTS shortlists (
            id TEXT PRIMARY KEY,
            club_id TEXT,
            partner_id TEXT,
            score REAL,
            created_at TEXT DEFAULT (datetime('now')),
            FOREIGN KEY (club_id) REFERENCES clubs(id),
            FOREIGN KEY (partner_id) REFERENCES partners(id)
        )
    """)
    
    conn.commit()
    conn.close()
    print(f"✅ DB initialisée: {DB_PATH}")

if __name__ == "__main__":
    init_db()
