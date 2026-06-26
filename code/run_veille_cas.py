"""
Veille quotidienne enrichie des cas inspirants.
Sources : Stade Bordelais, Label Sport Impact, LinkedIn, Sporsora, Fair Play For Planet, web.
"""

import sys
import json
import sqlite3
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent))
from veille_cas_inspirants import ajouter_cas, prochain_id, statistiques

DB_PATH = "data/territoiresport.db"


def search_web(query: str, max_results: int = 5):
    """Lance une recherche web (à implémenter avec web_search)."""
    print(f"🔍 Recherche : {query}")
    # En production : return web_search(query, max_results)
    return []


def veille_stade_bordelais():
    """Surveille les nouveaux projets du Stade Bordelais via leur newsletter."""
    print("\n📰 Veille Stade Bordelais...")
    results = search_web("Stade Bordelais S'engage newsletter nouveau projet")
    # Parser les résultats pour extraire les nouveaux cas
    return results


def veille_label_sport_impact():
    """Surveille les nouveaux clubs labellisés Label Sport Impact."""
    print("\n🏷️  Veille Label Sport Impact...")
    results = search_web("Label Sport Impact nouveau club labellisé 2026")
    return results


def veille_sporsora():
    """Surveille les études Sporsora sur le sport responsable."""
    print("\n📊 Veille Sporsora...")
    results = search_web("Sporsora sponsoring responsable sport étude 2026")
    return results


def veille_fair_play_for_planet():
    """Surveille les initiatives Fair Play For Planet."""
    print("\n🌱 Veille Fair Play For Planet...")
    results = search_web("Fair Play For Planet club sportif engagement écologique")
    return results


def veille_linkedin_contacts():
    """Surveille les posts LinkedIn des contacts clés."""
    print("\n💼 Veille LinkedIn...")
    contacts = [
        "Fayçal Jelil À Vos Parcours",
        "Clément Gorce Label Sport Impact",
        "Stade Bordelais S'engage",
    ]
    for contact in contacts:
        results = search_web(f"{contact} LinkedIn nouveau projet")
    return []


def veille_web_generique():
    """Recherche générique de nouveaux cas inspirants."""
    print("\n🌐 Veille web générique...")
    queries = [
        "club sportif amateur projet sociétal inspirant 2026",
        "association sportive inclusion handicap nouveau dispositif",
        "club football rugby basketball projet environnemental France",
    ]
    for q in queries:
        search_web(q)
    return []


def ajouter_cas_depuis_resultats(results, source_name):
    """Parse les résultats web et ajoute les cas pertinents en BDD."""
    # En production : parsing intelligent des résultats
    # Pour l'instant : structure placeholder
    pass


def generer_rapport_veille(nouveaux_cas_ids):
    """Génère un rapport de veille."""
    stats = statistiques()
    rapport = f"""
🔍 **Veille cas inspirants — {datetime.now().strftime('%d/%m/%Y')}**

**Nouveaux cas ajoutés :** {len(nouveaux_cas_ids)}
{chr(10).join(f'  - {cid}' for cid in nouveaux_cas_ids)}

**Base totale :** voir stats ci-dessus
"""
    return rapport


def main():
    """Lance toutes les veilles."""
    print("=" * 60)
    print("🔍 VEILLE QUOTIDIENNE ENRICHIE — CAS INSPIRANTS")
    print("=" * 60)

    stats_init = statistiques()

    # Lancer toutes les veilles
    veille_stade_bordelais()
    veille_label_sport_impact()
    veille_sporsora()
    veille_fair_play_for_planet()
    veille_linkedin_contacts()
    veille_web_generique()

    print("\n✅ Veille terminée")
    statistiques()


if __name__ == "__main__":
    main()