"""Seed de la base TerritoireSport."""
import sqlite3
import json
import uuid
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
    cur.execute("SELECT club_id FROM diagnostics WHERE club_id = ?", (club_id,))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO diagnostics (id, club_id, score, profile, answers, completed_at)
            VALUES (?, ?, ?, ?, ?, datetime('now'))
        """, (
            str(uuid.uuid4()),
            club_id,
            15,
            "engaged",
            json.dumps({
                "axes_prioritaires": [
                    "Développer les partenariats privés",
                    "Renforcer la communication digitale",
                    "Diversifier les sources de financement"
                ]
            })
        ))
        print(f"✅ Diagnostic créé : score 15/20, profil engaged")

    # ── 3. Territoire ───────────────────────────────────────────
    cur.execute("SELECT id FROM territories WHERE id = ?", ("argentan-intercom",))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO territories (id, name, type, department, region, population, description)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "argentan-intercom",
            "Argentan Intercom",
            "epci",
            "61",
            "Normandie",
            16850,
            "Bassin de vie rural du nord-ouest de l'Orne, marqué par des indicateurs socio-économiques fragiles et la présence d'un QPV."
        ))
        print(f"✅ Territoire créé : Argentan Intercom")

    # ── 4. Acteurs du territoire ────────────────────────────────
    actors_path = Path("data/territory_actors.json")
    if actors_path.exists():
        actors = json.loads(actors_path.read_text())
        for a in actors:
            cur.execute("SELECT id FROM partners WHERE name = ? AND city = ?", (a["name"], a.get("city", "Argentan")))
            if not cur.fetchone():
                cur.execute("""
                    INSERT INTO partners (id, name, type, category, city, department, themes, contact_email, contact_url, description)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    str(uuid.uuid4()),
                    a["name"],
                    a.get("type", "acteur_territorial"),
                    a.get("category", "institution"),
                    a.get("city", "Argentan"),
                    a.get("department", "61"),
                    json.dumps(a.get("themes", [])),
                    a.get("email"),
                    a.get("url"),
                    a.get("description")
                ))
        cur.execute("SELECT COUNT(*) FROM partners WHERE city = 'Argentan'")
        nb_actors = cur.fetchone()[0]
        print(f"✅ {nb_actors} acteurs territoriaux (Argentan) — depuis JSON")

    # ── 5. Partenaires ──────────────────────────────────────────
    partners_path = Path("data/partners.json")
    if partners_path.exists():
        partners = json.loads(partners_path.read_text())
    else:
        # Partenaires par défaut
        partners = [
            {"name": "Crédit Mutuel de Bretagne", "type": "sponsor", "category": "banque", "city": "Caen", "department": "14", "themes": ["Sponsoring"], "email": "contact@cmb.fr", "url": "https://www.cmb.fr"},
            {"name": "Decathlon Pro", "type": "fournisseur", "category": "equipementier", "city": "Caen", "department": "14", "themes": ["Equipement sportif"], "email": "pro@decathlon.fr", "url": "https://www.decathlonpro.fr"},
            {"name": "Région Normandie", "type": "institution", "category": "collectivite", "city": "Caen", "department": "14", "themes": ["Sport & Santé", "Formation"], "email": "contact@normandie.fr", "url": "https://www.normandie.fr"},
            {"name": "DDCS du Calvados", "type": "institution", "category": "etat", "city": "Caen", "department": "14", "themes": ["Politique sportive"], "email": "ddcs@calvados.gouv.fr", "url": None},
            {"name": "CROS Normandie", "type": "federation", "category": "sport", "city": "Caen", "department": "14", "themes": ["Olympisme", "Formation"], "email": "cros@normandie.fr", "url": "https://cros-normandie.fr"},
            {"name": "Agence Nationale du Sport", "type": "institution", "category": "etat", "city": "Paris", "department": "75", "themes": ["Financement sport"], "email": "contact@ans.fr", "url": "https://www.ans.fr"},
            {"name": "Fondation de France", "type": "fondation", "category": "mecénat", "city": "Paris", "department": "75", "themes": ["Mécénat", "Inclusion"], "email": "contact@fdf.org", "url": "https://www.fondationdefrance.org"}
        ]
    for p in partners:
        cur.execute("SELECT id FROM partners WHERE name = ?", (p["name"],))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO partners (id, name, type, category, city, department, contact_email, contact_url, description, themes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), p["name"], p["type"], p.get("category"), p["city"], p["department"], p.get("email"), p.get("url"), p.get("description"), json.dumps(p.get("themes", []))))
    cur.execute("SELECT COUNT(*) FROM partners")
    nb_partners = cur.fetchone()[0]
    print(f"✅ {nb_partners} partenaires créés")
    # ── 5b. Scoring des partenaires ─────────────────────────────
    type_scores = {
        "institution": 30,
        "sponsor": 25,
        "federation": 20,
        "fondation": 25,
        "fournisseur": 10,
        "acteur_territorial": 15,
        "association": 20,
        "public": 25
    }
    club_commune = "Argentan"
    cur.execute("SELECT id, type, city, themes, category FROM partners WHERE score = 0 OR score IS NULL")
    partners_to_score = cur.fetchall()
    for p in partners_to_score:
        pid, ptype, city, themes_json, category = p
        score = type_scores.get(ptype, 5)
        if city == club_commune:
            score += 20
        if themes_json:
            try:
                partner_themes = json.loads(themes_json)
                score += min(len(partner_themes) * 5, 20)
            except:
                pass
        if category == "sport":
            score += 10
        cur.execute("UPDATE partners SET score = ? WHERE id = ?", (score, pid))
    if partners_to_score:
        print(f"✅ {len(partners_to_score)} partenaires scorés")

    # ── 5b. Scoring des partenaires ─────────────────────────────
    type_scores = {
        "institution": 30,
        "sponsor": 25,
        "federation": 20,
        "fondation": 25,
        "fournisseur": 10,
        "acteur_territorial": 15,
        "association": 20,
        "public": 25
    }
    club_commune = "Argentan"
    cur.execute("SELECT id, type, city, themes, category FROM partners WHERE score = 0 OR score IS NULL")
    partners_to_score = cur.fetchall()
    for p in partners_to_score:
        pid, ptype, city, themes_json, category = p
        score = type_scores.get(ptype, 5)
        if city == club_commune:
            score += 20
        if themes_json:
            try:
                partner_themes = json.loads(themes_json)
                score += min(len(partner_themes) * 5, 20)
            except:
                pass
        if category == "sport":
            score += 10
        cur.execute("UPDATE partners SET score = ? WHERE id = ?", (score, pid))
    if partners_to_score:
        print(f"✅ {len(partners_to_score)} partenaires scorés")


    # ── 6. Projets de la bibliothèque ───────────────────────────
    library_path = Path("data/projects_library.json")
    if library_path.exists():
        library = json.loads(library_path.read_text())
        cur.execute("SELECT COUNT(*) FROM projects")
        nb_projects_db = cur.fetchone()[0]
        if nb_projects_db == 0:
            for proj in library:
                cur.execute("""
                    INSERT INTO projects (id, club_id, title, description, themes, budget, status)
                    VALUES (?, ?, ?, ?, ?, ?, 'library')
                """, (str(uuid.uuid4()), club_id, proj.get("title"), proj.get("description"), json.dumps(proj.get("themes", [])), proj.get("budget")))
        cur.execute("SELECT COUNT(*) FROM projects")
        nb_library = cur.fetchone()[0]
        print(f"✅ {nb_library} projets de bibliothèque (depuis JSON)")

    # ── 7. Sources de financement ───────────────────────────────
    fundings = [
        {
            "name": "ANS — Projets sportifs territoriaux",
            "type": "subvention",
            "organization": "Agence Nationale du Sport",
            "themes": ["Sport & Santé", "Inclusion"],
            "min": 5000, "max": 50000,
            "deadline": "2026-09-30",
            "url": "https://www.ans.fr/appels-a-projets",
            "description": "Soutien aux projets sportifs à impact territorial",
            "eligibility": "Clubs affiliés FFSport, EAPS, collectivités"
        },
        {
            "name": "Région Normandie — Aide aux clubs",
            "type": "subvention",
            "organization": "Région Normandie",
            "themes": ["Formation", "Equipement"],
            "min": 2000, "max": 20000,
            "deadline": "2026-12-31",
            "url": "https://www.normandie.fr",
            "description": "Aide régionale au fonctionnement des clubs sportifs normands",
            "eligibility": "Clubs normands affiliés fédération"
        },
        {
            "name": "Fondation de France — Sport & Inclusion",
            "type": "fondation",
            "organization": "Fondation de France",
            "themes": ["Inclusion", "Handicap"],
            "min": 10000, "max": 100000,
            "deadline": "2027-02-15",
            "url": "https://www.fondationdefrance.org",
            "description": "Soutien aux projets favorisant l'accès au sport pour publics fragiles",
            "eligibility": "Associations loi 1901, 2 ans d'ancienneté"
        },
        {
            "name": "CPAM Calvados — Sport en Santé",
            "type": "subvention",
            "organization": "CPAM du Calvados",
            "themes": ["Sport & Santé"],
            "min": 1000, "max": 10000,
            "deadline": "2026-06-30",
            "url": "https://www.ameli.fr",
            "description": "AAP Sport en Santé pour associations du Calvados",
            "eligibility": "Associations loi 1901 du Calvados"
        }
    ]
    for f in fundings:
        cur.execute("SELECT id FROM funding_sources WHERE name = ?", (f["name"],))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO funding_sources (id, name, type, organization, themes, amount_min, amount_max, deadline, url, description, eligibility_criteria)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (str(uuid.uuid4()), f["name"], f["type"], f["organization"], json.dumps(f["themes"]), f["min"], f["max"], f["deadline"], f["url"], f["description"], f["eligibility"]))
    print(f"✅ {len(fundings)} sources de financement créées")

    # ── 8. Projets inspirants ───────────────────────────────────
    insp_path = Path("data/cas_inspirants.json")
    if insp_path.exists():
        insp = json.loads(insp_path.read_text())
        print(f"✅ {len(insp)} cas inspirants (depuis JSON)")

    # ── 9. Projets du club BATT (exemples) ───────────────────────
    projets_batt = [
        {
            "title": "Ping pour Tous — Inclusion par le tennis de table",
            "description": "Programme d'inclusion sociale par le tennis de table ciblant seniors, personnes en situation de handicap et jeunes en décrochage.",
            "themes": ["Insertion / Cohésion Sociale", "Sport & Santé", "Handicap"],
            "budget": 15000
        },
        {
            "title": "Tournoi Intergénérationnel de l'Orne",
            "description": "Tournoi annuel ouvert aux familles, écoles et EHPAD du territoire.",
            "themes": ["Lien Intergénérationnel", "Animation Territoriale"],
            "budget": 5000
        },
        {
            "title": "Cogni-Ping — Performance & Rééducation",
            "description": "Programme de recherche appliquée sur les liens entre cognition, anticipation et performance au tennis de table.",
            "themes": ["Recherche", "Performance", "Innovation"],
            "budget": 80000
        },
        {
            "title": "Section Sport-Santé — Tennis de Table & Parkinson",
            "description": "Section dédiée aux personnes atteintes de la maladie de Parkinson, en partenariat avec l'IME de Caen et Handisport 14.",
            "themes": ["Sport & Santé", "Handicap", "Maladies Neurodégénératives"],
            "budget": 12000
        }
    ]
    for p in projets_batt:
        cur.execute("SELECT id FROM projects WHERE title = ? AND club_id = ?", (p["title"], club_id))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO projects (id, club_id, title, description, themes, budget, status)
                VALUES (?, ?, ?, ?, ?, ?, 'active')
            """, (str(uuid.uuid4()), club_id, p["title"], p["description"], json.dumps(p["themes"]), p["budget"]))
    cur.execute("SELECT COUNT(*) FROM projects WHERE club_id = ?", (club_id,))
    nb_projets_batt = cur.fetchone()[0]
    print(f"✅ {nb_projets_batt} projets pour le club BATT")

    # ── 10. Liaison club-territoire ─────────────────────────────
    cur.execute("SELECT territory_id FROM club_territories WHERE club_id = ?", (club_id,))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO club_territories (club_id, territory_id, is_primary)
            VALUES (?, ?, 1)
        """, (club_id, "argentan-intercom"))
        print(f"✅ Territoire lié : Argentan Intercom")

    conn.commit()
    conn.close()
    print("\n🎉 Seed terminé avec succès")


if __name__ == "__main__":
    seed()


# ── 11. Clubs supplémentaires (démonstration multi-clubs) ─────
clubs_demo = [
    {
        "name": "Stade Malherbe Caen — Section Tennis de Table",
        "sport": "tennis_de_table",
        "city": "Caen",
        "commune": "Caen",
        "epci": "Caen la Mer",
        "department": "14",
        "size": "large",
        "contact_email": "tt@smcaen.fr",
        "contact_phone": "02 31 29 12 34"
    },
    {
        "name": "Hockey Club de Caen",
        "sport": "hockey_sur_glace",
        "city": "Caen",
        "commune": "Caen",
        "epci": "Caen la Mer",
        "department": "14",
        "size": "medium",
        "contact_email": "contact@hcc.fr",
        "contact_phone": "02 31 45 67 89"
    },
    {
        "name": "USO Mondeville Basket",
        "sport": "basketball",
        "city": "Mondeville",
        "commune": "Mondeville",
        "epci": "Caen la Mer",
        "department": "14",
        "size": "medium",
        "contact_email": "basket@uso-mondeville.fr",
        "contact_phone": "02 31 78 90 12"
    },
    {
        "name": "Stade Caennais Rugby Club",
        "sport": "rugby",
        "city": "Caen",
        "commune": "Caen",
        "epci": "Caen la Mer",
        "department": "14",
        "size": "medium",
        "contact_email": "contact@stade-caennais.fr",
        "contact_phone": "02 31 34 56 78"
    },
    {
        "name": "Caen Padel Club",
        "sport": "padel",
        "city": "Caen",
        "commune": "Caen",
        "epci": "Caen la Mer",
        "department": "14",
        "size": "small",
        "contact_email": "contact@caenpadel.fr",
        "contact_phone": "02 31 56 78 90"
    }
]

import sqlite3
import uuid as _uuid
conn = sqlite3.connect(DB_PATH)
cur = conn.cursor()
for c in clubs_demo:
    cur.execute("SELECT id FROM clubs WHERE name = ?", (c["name"],))
    if not cur.fetchone():
        cur.execute("""
            INSERT INTO clubs (id, name, sport, city, commune, epci, department, size, contact_email, contact_phone, password_hash, created_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, datetime('now'))
        """, (
            str(_uuid.uuid4()),
            c["name"],
            c["sport"],
            c["city"],
            c["commune"],
            c["epci"],
            c["department"],
            c["size"],
            c["contact_email"],
            c["contact_phone"],
            "demo_hash_" + c["sport"]
        ))
conn.commit()
cur.execute("SELECT COUNT(*) FROM clubs")
nb_clubs = cur.fetchone()[0]
print(f"✅ {nb_clubs} clubs en base (incluant {len(clubs_demo)} nouveaux)")
conn.close()
