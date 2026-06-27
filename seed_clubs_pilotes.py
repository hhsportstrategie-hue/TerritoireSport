"""
Seed des 3 clubs pilotes TerritoireSport.

Crée dans la table `clubs` (utilisée par le parcours) :
- BATT (Bayard Argentan Tennis de Table) - Tennis de table - Argentan (Orne)
- ES Coutances Football - Football - Coutances (Manche)
- AS Cherbourg Football - Football - Cherbourg (Manche)

Crée aussi un projet pré-rempli pour chaque club (référencés dans le parcours).
"""
import sqlite3
import secrets
import json
from datetime import datetime, timezone
from db_config import DB_PATH



DEPT_CODES = {
    "Calvados": "14",
    "Eure": "27",
    "Manche": "50",
    "Orne": "61",
    "Seine-Maritime": "76",
    "Paris": "75",
}

def _now_iso():
    return datetime.now(timezone.utc).isoformat()


def _hash_password(password: str) -> str:
    """Match hash utilisé par parcours.py : SHA256 sans sel."""
    import hashlib
    return hashlib.sha256(password.encode()).hexdigest()


def _ensure_schema():
    """Crée les tables nécessaires si absentes."""
    conn = sqlite3.connect(DB_PATH)
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS clubs (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            sport TEXT,
            city TEXT,
            department TEXT,
            members_count INTEGER,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS engineering_projects (
            id TEXT PRIMARY KEY,
            club_id TEXT NOT NULL,
            title TEXT NOT NULL,
            description TEXT,
            theme_id TEXT,
            public_cible TEXT,
            objectifs TEXT,
            budget_estimate REAL,
            step INTEGER DEFAULT 1,
            status TEXT DEFAULT 'draft',
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            FOREIGN KEY (club_id) REFERENCES clubs(id)
        );
    """)
    conn.commit()
    conn.close()


def _seed_club(name, email, password, sport, city, department, members_count):
    """Crée un club s'il n'existe pas déjà."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT id, password_hash FROM clubs WHERE email = ?", (email,))
    existing = cur.fetchone()
    if existing:
        # Mettre à jour le mot de passe si différent (corrige anciens seeds avec hash incorrect)
        new_hash = _hash_password(password)
        if existing["password_hash"] != new_hash:
            cur.execute("UPDATE clubs SET password_hash = ? WHERE id = ?", (new_hash, existing["id"]))
            conn.commit()
            print(f"  ↻ {name} existe — mot de passe mis à jour (id={existing['id']})")
        else:
            print(f"  ↻ {name} existe déjà (id={existing['id']})")
        conn.close()
        return existing["id"]

    club_id = f"club-{secrets.token_hex(6)}"
    cur.execute(
        """INSERT INTO clubs
           (id, name, email, password_hash, sport, city, department, members_count, created_at)
           VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)""",
        (club_id, name, email, _hash_password(password), sport, city, department, members_count, _now_iso())
    )
    conn.commit()
    conn.close()
    print(f"  ✓ {name} créé (id={club_id})")
    return club_id


def _seed_project(club_id, title, description, theme_id, public_cible, objectifs, budget_estimate):
    """Crée un projet d'ingénierie pour un club."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    # Vérifier si un projet avec ce titre existe déjà pour ce club
    cur.execute(
        "SELECT id FROM engineering_projects WHERE club_id = ? AND objectifs LIKE ?",
        (club_id, f"%{objectifs[:30]}%")
    )
    existing = cur.fetchone()
    if existing:
        print(f"    ↻ Projet '{title}' existe déjà")
        conn.close()
        return existing["id"]

    project_id = f"proj-{secrets.token_hex(6)}"
    cur.execute(
        """INSERT INTO engineering_projects
           (id, club_id, theme_id, public_cible, objectifs, activites, status, current_step, created_at, updated_at)
           VALUES (?, ?, ?, ?, ?, ?, 'active', 2, ?, ?)""",
        (project_id, club_id, theme_id, public_cible, objectifs,
         f"DESCRIPTION: {description}\n\nBUDGET_ESTIMATE: {budget_estimate}",
         _now_iso(), _now_iso())
    )
    conn.commit()
    conn.close()
    print(f"    ✓ Projet '{title}' créé (id={project_id})")
    return project_id


def main():
    print("=" * 70)
    print("SEED CLUBS PILOTES TERRITOIRESPORT")
    print("=" * 70)
    print()

    _ensure_schema()

    # ─── 1. BATT (Tennis de table - Argentan) ───
    print("1. BATT - Bayard Argentan Tennis de Table")
    batt_id = _seed_club(
        name="BATT - Bayard Argentan Tennis de Table",
        email="contact@batt-argentan.fr",
        password="batt2026",
        sport="Tennis de table",
        city="Argentan",
        department=DEPT_CODES["Orne"],
        members_count=85,
    )
    _seed_project(
        club_id=batt_id,
        title="Ping pour Tous - Inclusion par le tennis de table",
        description=(
            "Programme d'inclusion sociale, lien intergénérationnel et "
            "insertion professionnelle via le tennis de table. "
            "Ateliers ciblant seniors, personnes handicapées et jeunes en décrochage."
        ),
        theme_id="handicap",
        public_cible="Seniors, personnes en situation de handicap, jeunes en décrochage scolaire",
        objectifs=(
            "• Lutter contre l'isolement des seniors\n"
            "• Favoriser la mixité intergénérationnelle\n"
            "• Transmettre les savoirs via le sport\n"
            "• Créer un pont vers l'emploi pour les jeunes"
        ),
        budget_estimate=3000,
    )
    print()

    # ─── 2. ES Coutances Football ───
    print("2. ES Coutances Football")
    coutances_id = _seed_club(
        name="ES Coutances Football",
        email="contact@es-coutances-football.fr",
        password="coutances2026",
        sport="Football",
        city="Coutances",
        department=DEPT_CODES["Manche"],
        members_count=240,
    )
    _seed_project(
        club_id=coutances_id,
        title="Développement du sponsoring et mécénat local",
        description=(
            "Structurer la stratégie de partenariats privés du club : "
            "sponsoring entreprises locales, mécénat, hospitalités. "
            "Objectif : doubler les revenus B2B en 2 saisons."
        ),
        theme_id="economie",
        public_cible="Entreprises locales du Coutançais, dirigeants TPE/PME",
        objectifs=(
            "• Cartographier 100 prospects B2B ciblés\n"
            "• Construire une offre de sponsoring modulaire\n"
            "• Animer un Club Partenaires annuel\n"
            "• Mesurer le ROI pour chaque partenaire"
        ),
        budget_estimate=8000,
    )
    print()

    # ─── 3. AS Cherbourg Football ───
    print("3. AS Cherbourg Football")
    cherbourg_id = _seed_club(
        name="AS Cherbourg Football",
        email="contact@as-cherbourg-football.fr",
        password="cherbourg2026",
        sport="Football",
        city="Cherbourg-en-Cotentin",
        department=DEPT_CODES["Manche"],
        members_count=320,
    )
    _seed_project(
        club_id=cherbourg_id,
        title="Insertion professionnelle par le football (type XV pour l'Emploi)",
        description=(
            "Dispositif d'insertion professionnelle pour jeunes 18-25 ans "
            "inspiré du modèle XV pour l'Emploi (Caen). "
            "3 mois : orientation, compétences, stage entreprise, suivi 1 an."
        ),
        theme_id="insertion",
        public_cible="Jeunes 18-25 ans éloignés de l'emploi, quartier Nord Cherbourg",
        objectifs=(
            "• Accompagner 15 jeunes par promotion\n"
            "• 80% en situation pro à l'issue (CDI/CDD/formation)\n"
            "• Créer un réseau d'entreprises d'accueil locales\n"
            "• Pérenniser le dispositif sur 3 ans"
        ),
        budget_estimate=25000,
    )
    print()

    # ─── 4. Récap final ───
    print("=" * 70)
    print("RÉCAPITULATIF")
    print("=" * 70)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cur = conn.cursor()

    cur.execute("SELECT id, name, email, sport, city FROM clubs ORDER BY created_at DESC LIMIT 5")
    clubs = cur.fetchall()
    print(f"\n📋 {len(clubs)} clubs récents :")
    for c in clubs:
        print(f"   • {c['name']} ({c['sport']}, {c['city']})")
        print(f"     Email: {c['email']}")

    cur.execute("SELECT id, club_id, theme_id, activites FROM engineering_projects ORDER BY created_at DESC LIMIT 5")
    projects = cur.fetchall()
    print(f"\n📋 {len(projects)} projets récents :")
    for p in projects:
        activite = (p['activites'] or '')[:60]
        print(f"   • Thème {p['theme_id']}: {activite}...")

    conn.close()

    print()
    print("=" * 70)
    print("IDENTIFIANTS DE CONNEXION")
    print("=" * 70)
    print()
    print("🔑 BATT Argentan")
    print("   Email:    contact@batt-argentan.fr")
    print("   Password: batt2026")
    print()
    print("🔑 ES Coutances")
    print("   Email:    contact@es-coutances-football.fr")
    print("   Password: coutances2026")
    print()
    print("🔑 AS Cherbourg")
    print("   Email:    contact@as-cherbourg-football.fr")
    print("   Password: cherbourg2026")
    print()
    print("🌐 Page parcours : https://ts-backend-production.up.railway.app/parcours")
    print()


if __name__ == "__main__":
    main()
