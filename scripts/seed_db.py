#!/usr/bin/env python3
"""
Seed script — initialise la base de données TerritoireSport.

Usage :
    python3 scripts/seed_db.py

Ce script :
1. Vérifie si la DB est vide
2. Si oui : importe les données depuis data/*.json
3. Sinon : ne fait rien (préserve les données existantes)
"""
import asyncio
import json
import os
import sys
from pathlib import Path

import aiosqlite

# Ajouter le répertoire parent au path
sys.path.insert(0, str(Path(__file__).parent.parent))

from db_config import DB_PATH


async def seed_partners(db):
    """Importe les partenaires depuis data/base_consolidee_epci.json."""
    partners_file = Path("data/base_consolidee_epci.json")
    if not partners_file.exists():
        print(f"⚠️  {partners_file} introuvable — skip")
        return 0

    with open(partners_file) as f:
        partners = json.load(f)

    count = 0
    for p in partners:
        try:
            await db.execute(
                """INSERT OR IGNORE INTO partners
                   (id, name, type, theme, city, department, contact_email, contact_phone, description, themes)
                   VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
                (
                    p.get("id"),
                    p.get("name"),
                    p.get("type"),
                    p.get("theme"),
                    p.get("city"),
                    p.get("department"),
                    p.get("contact_email"),
                    p.get("contact_phone"),
                    p.get("description"),
                    json.dumps(p.get("themes", [])),
                ),
            )
            count += 1
        except Exception as e:
            print(f"⚠️  Erreur import partenaire {p.get('name')}: {e}")

    await db.commit()
    return count


async def seed_communes(db):
    """Importe les communes depuis data/communes_normandie.json."""
    communes_file = Path("data/communes_normandie.json")
    if not communes_file.exists():
        print(f"⚠️  {communes_file} introuvable — skip")
        return 0

    with open(communes_file) as f:
        communes = json.load(f)

    count = 0
    for c in communes:
        try:
            await db.execute(
                """INSERT OR IGNORE INTO communes
                   (code_insee, name, department, epci_code, population, latitude, longitude)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    c.get("code_insee"),
                    c.get("name"),
                    c.get("department"),
                    c.get("epci_code"),
                    c.get("population"),
                    c.get("latitude"),
                    c.get("longitude"),
                ),
            )
            count += 1
        except Exception as e:
            print(f"⚠️  Erreur import commune {c.get('name')}: {e}")

    await db.commit()
    return count


async def seed_epcis(db):
    """Importe les EPCI depuis data/epcis_normandie.json."""
    epcis_file = Path("data/epcis_normandie.json")
    if not epcis_file.exists():
        print(f"⚠️  {epcis_file} introuvable — skip")
        return 0

    with open(epcis_file) as f:
        epcis = json.load(f)

    count = 0
    for e in epcis:
        try:
            await db.execute(
                """INSERT OR IGNORE INTO epcis
                   (code, name, department, population, superficie)
                   VALUES (?, ?, ?, ?, ?)""",
                (
                    e.get("code"),
                    e.get("name"),
                    e.get("department"),
                    e.get("population"),
                    e.get("superficie"),
                ),
            )
            count += 1
        except Exception as e:
            print(f"⚠️  Erreur import EPCI {e.get('name')}: {e}")

    await db.commit()
    return count


async def main():
    """Point d'entrée principal."""
    print(f"🌱 Seed DB : {DB_PATH}")

    # Vérifier que la DB existe (créée par init_db)
    if not Path(DB_PATH).exists():
        print(f"❌ DB introuvable : {DB_PATH}")
        print("   Lance d'abord : python3 -c 'from main import init_db; import asyncio; asyncio.run(init_db())'")
        return 1

    async with aiosqlite.connect(DB_PATH) as db:
        # Vérifier si la table partners est vide
        async with db.execute("SELECT COUNT(*) FROM partners") as cur:
            partners_count = (await cur.fetchone())[0]

        if partners_count > 0:
            print(f"✅ DB déjà seedée ({partners_count} partenaires) — skip")
            return 0

        print("📥 Import des données...")
        n_partners = await seed_partners(db)
        print(f"   ✅ {n_partners} partenaires importés")

        n_communes = await seed_communes(db)
        print(f"   ✅ {n_communes} communes importées")

        n_epcis = await seed_epcis(db)
        print(f"   ✅ {n_epcis} EPCI importés")

    print("🎉 Seed terminé !")
    return 0


if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)