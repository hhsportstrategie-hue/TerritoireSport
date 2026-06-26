"""
Veille quotidienne des cas inspirants pour TerritoireSport.

Sources surveillées :
- Newsletter 'Le Stade S'engage' (Stade Bordelais)
- Label Sport Impact (annuaire + actualités)
- LinkedIn (Fayçal Jelil, Clément Gorce, etc.)
- Sporsora, Fair Play For Planet
- Web search générique

Crée un nouveau cas inspirant dans la base si pertinent.
"""

import sqlite3
import json
import sys
from pathlib import Path
from datetime import datetime

DB_PATH = "data/territoiresport.db"


def ajouter_cas(cas_data: dict):
    """Ajoute un cas inspirant à la base."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    try:
        cur.execute("""
            INSERT OR IGNORE INTO cas_inspirants (
                id, section, type_source, titre, structure, niveau_club,
                thematiques, description, ressources, partenaires, resultats,
                budget_reel, adaptation_club_amateur, transposabilite, reproductibilite,
                source, date_detection
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            cas_data['id'], cas_data['section'], cas_data['type_source'],
            cas_data['titre'], cas_data['structure'], cas_data['niveau_club'],
            json.dumps(cas_data['thematiques']), cas_data['description'],
            cas_data.get('ressources', ''), json.dumps(cas_data.get('partenaires', [])),
            cas_data.get('resultats', ''), cas_data.get('budget_reel'),
            cas_data.get('adaptation_club_amateur', ''),
            cas_data.get('transposabilite', 'adaptable'),
            cas_data.get('reproductibilite', 'moyen'),
            cas_data.get('source', ''), cas_data.get('date_detection', datetime.now().strftime('%Y-%m-%d'))
        ))
        conn.commit()
        if cur.rowcount > 0:
            print(f"✅ Nouveau cas ajouté : {cas_data['id']} - {cas_data['titre']}")
            return True
        else:
            print(f"⏭️  Cas déjà existant : {cas_data['id']}")
            return False
    except Exception as e:
        print(f"❌ Erreur pour {cas_data['id']}: {e}")
        return False
    finally:
        conn.close()


def prochain_id():
    """Génère le prochain ID disponible (CAS-021, CAS-022...)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT MAX(CAST(SUBSTR(id, 5) AS INTEGER)) FROM cas_inspirants WHERE id LIKE 'CAS-%'")
    result = cur.fetchone()[0]
    conn.close()
    next_num = (result or 0) + 1
    return f"CAS-{next_num:03d}"


def statistiques():
    """Affiche les stats de la base."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM cas_inspirants")
    total = cur.fetchone()[0]
    cur.execute("SELECT section, COUNT(*) FROM cas_inspirants GROUP BY section")
    by_section = cur.fetchall()
    cur.execute("SELECT source, COUNT(*) FROM cas_inspirants GROUP BY source ORDER BY 2 DESC LIMIT 5")
    by_source = cur.fetchall()
    conn.close()
    print(f"\n📊 Stats base cas_inspirants :")
    print(f"   Total : {total}")
    print(f"   Par section :")
    for s, c in by_section:
        print(f"     - {s}: {c}")
    print(f"   Top sources :")
    for s, c in by_source:
        print(f"     - {s}: {c}")


if __name__ == "__main__":
    # Stats actuelles
    statistiques()
    print(f"\n🆔 Prochain ID disponible : {prochain_id()}")