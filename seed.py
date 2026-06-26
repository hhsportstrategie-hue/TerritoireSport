"""
Script de seed — Peuple la base avec des données de démonstration complètes.
Idempotent : peut être exécuté plusieurs fois sans dupliquer.
"""
import sqlite3
import uuid
import json
import os
from pathlib import Path

DB_PATH = os.getenv("DB_PATH", os.path.join(os.path.dirname(os.path.abspath(__file__)), "data", "territoiresport.db"))


def seed():
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # ── 0. Communes normandes ───────────────────────────────────
    communes_path = Path("data/communes_normandie.json")
    if communes_path.exists():
        communes_data = json.loads(communes_path.read_text())
        for c in communes_data:
            cur.execute("SELECT id FROM communes WHERE code_insee = ?", (c.get("code"),))
            if not cur.fetchone():
                centre = c.get("centre") or {}
                coords = centre.get("coordinates") if isinstance(centre, dict) else None
                lat = coords[1] if isinstance(coords, list) and len(coords) >= 2 else None
                lon = coords[0] if isinstance(coords, list) and len(coords) >= 2 else None
                cur.execute("""
                    INSERT INTO communes (id, name, code_insee, department, population, latitude, longitude, epci)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    c.get("nom"),
                    c.get("code"),
                    c.get("codeDepartement"),
                    c.get("population"),
                    lat,
                    lon,
                    c.get("codeEpci")
                ))
        conn.commit()
        cur.execute("SELECT COUNT(*) FROM communes")
        nb_communes = cur.fetchone()[0]
        print(f"✅ {nb_communes} communes normandes en base")

    # ── 1. Club de démonstration ─────────────────────────────────
    club_id = "90f8a193-a4b8-4975-b315-8e1484cdf3a3"
    cur.execute("SELECT id FROM clubs WHERE id = ?", (club_id,))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO clubs (id, name, sport, city, commune, epci, department, size, contact_email, contact_phone, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            club_id,
            "BATT Argentan — Bayard Argentan Tennis de Table",
            "tennis_de_table",
            "Argentan",
            "Argentan",
            "Argentan Intercom",
            "61",
            "medium",
            "contact@batt-argentan.fr",
            "02 33 12 34 56",
            "demo_hash_batt",
        ))
        print(f"✅ Club créé : BATT Argentan ({club_id})")

    # ── 2. Diagnostic ───────────────────────────────────────────
    cur.execute("SELECT id FROM diagnostics WHERE club_id = ?", (club_id,))
    if not cur.fetchone():
        diag_id = str(uuid.uuid4())
        answers = {
            "q1": 2, "q2": 2, "q3": 1, "q4": 2, "q5": 2,
            "q6": 1, "q7": 2, "q8": 2, "q9": 1, "q10": 2,
        }
        cur.execute("""
            INSERT INTO diagnostics (id, club_id, answers, score, profile, completed_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (diag_id, club_id, json.dumps(answers), 15, "engaged"))
        print(f"✅ Diagnostic créé : score 15/20, profil engaged")

    cur.execute("SELECT territory_id FROM club_territories WHERE club_id = ?", (club_id,))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO club_territories (club_id, territory_id, is_primary)
            VALUES (?, ?, 1)
        """, (club_id, "argentan-intercom"))
        print(f"✅ Territoire lié : Argentan Intercom")
        print(f"✅ Territoire créé : Argentan Intercom")

    # ── 4. Acteurs du territoire ────────────────────────────────
    # Les acteurs sont stockés dans data/territory_actors.json (pas en DB)
    actors_path = Path("data/territory_actors.json")
    if actors_path.exists():
        actors_data = json.loads(actors_path.read_text())
        argentan_actors = [a for a in actors_data if a.get("territory_id") == "argentan-intercom"]
        print(f"✅ {len(argentan_actors)} acteurs territoriaux (Argentan) — depuis JSON")

    # ── 5. Partenaires ──────────────────────────────────────────
    partners = [
        ("Mairie de Ducey-Les Chéris", "public", "cohesion", "Ducey", "50", None, None,
         "Commune rurale de la Manche", ["cohesion", "education", "sante"]),
        ("DRAJES Normandie", "public", "insertion", "Caen", "14", None, "https://www.ac-normandie.fr",
         "Direction régionale académique à la jeunesse, à l'engagement et aux sports",
         ["insertion", "education", "haut_niveau"]),
        ("Ligue de Football de Normandie", "association", "amateur", "Caen", "14", None, "https://www.fff.fr",
         "Ligue régionale FFF — Normandie", ["amateur", "scolaire", "feminin"]),
        ("CINS Caen", "company", "numerique", "Caen", "14", None, None,
         "Agence digitale spécialisée sport", ["numerique", "gouvernance"]),
        ("ANS — Agence Nationale du Sport", "public", "sante", "Paris", "75", None,
         "https://www.agencedusport.fr",
         "Agence nationale du sport — financement et développement",
         ["sante", "insertion", "feminin", "handicap"]),
        ("Conseil Départemental de l'Orne", "public", "cohesion", "Alençon", "61", None,
         "https://www.orne.fr",
         "Collectivité départementale — soutien aux clubs et associations",
         ["cohesion", "scolaire", "amateur"]),
        ("Crédit Agricole Normandie", "company", "amateur", "Caen", "14", "partenariats@ca-normandie.fr",
         "https://www.ca-normandie.fr",
         "Banque régionale — sponsoring et partenariats clubs",
         ["amateur", "haut_niveau"]),
    ]
    for name, type_, category, city, dept, email, url, desc, themes in partners:
        cur.execute("SELECT id FROM partners WHERE name = ?", (name,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO partners (id, name, type, category, city, department,
                                      contact_email, contact_url, description, themes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), name, type_, category, city, dept, email, url, desc,
                  json.dumps(themes)))
    print(f"✅ {len(partners)} partenaires créés")

    # ── 6. Projets de la bibliothèque ───────────────────────────
    # La bibliothèque est stockée dans data/projects_library.json (pas en DB)
    lib_path = Path("data/projects_library.json")
    if lib_path.exists():
        lib = json.loads(lib_path.read_text())
        print(f"✅ {len(lib)} projets de bibliothèque (depuis JSON)")

    # ── 7. Sources de financement ───────────────────────────────
    fundings = [
        ("ANS — Projet Sportif Territorial", "public", "ANS",
         ["sante", "insertion", "handicap"], 5000, 50000, None,
         "https://www.agencedusport.fr/APA-projets",
         "Financement ANS pour projets sportifs territoriaux", None),
        ("Région Normandie — Sport & Cohésion", "public", "Région Normandie",
         ["cohesion", "education"], 3000, 30000, None,
         "https://www.normandie.fr",
         "AAP régional sport et cohésion sociale", None),
        ("Département de l'Orne — Vie associative", "public", "CD 61",
         ["amateur", "scolaire"], 1000, 10000, None,
         "https://www.orne.fr",
         "Soutien aux associations sportives ornaises", None),
        ("Fondation de France — Sport & Inclusion", "private", "Fondation de France",
         ["insertion", "handicap"], 2000, 20000, None,
         "https://www.fondationdefrance.org",
         "Mécénat pour projets sport et inclusion", None),
    ]
    for name, type_, org, themes, min_, max_, deadline, url, desc, elig in fundings:
        cur.execute("SELECT id FROM funding_sources WHERE name = ?", (name,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO funding_sources (id, name, type, organization, themes,
                                            amount_min, amount_max, deadline, url,
                                            description, eligibility_criteria)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), name, type_, org, json.dumps(themes),
                  min_, max_, deadline, url, desc, elig))
    print(f"✅ {len(fundings)} sources de financement créées")

    # ── 8. Projets inspirants ───────────────────────────────────
    # Les cas inspirants sont stockés dans data/cas_inspirants.json (pas en DB)
    insp_path = Path("data/cas_inspirants.json")
    if insp_path.exists():
        insp = json.loads(insp_path.read_text())
        print(f"✅ {len(insp)} cas inspirants (depuis JSON)")

    conn.commit()
    conn.close()
    print("\n🎉 Seed terminé avec succès")


if __name__ == "__main__":
    seed()