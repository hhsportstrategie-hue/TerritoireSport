"""
Script principal de veille quotidienne des cas inspirants.
Exécuté par le schedule quotidien.

Sources :
1. Web search sur les sources identifiées
2. Détection de nouveaux projets
3. Ajout automatique en BDD si pertinent
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))
from veille_cas_inspirants import ajouter_cas, prochain_id, statistiques


def veille_stade_bordelais():
    """Surveille les nouveaux projets du Stade Bordelais."""
    # À enrichir avec web_search + parsing newsletter
    pass


def veille_label_sport_impact():
    """Surveille les nouveaux clubs labellisés."""
    # À enrichir avec web_search + parsing annuaire
    pass


def veille_linkedin():
    """Surveille les posts LinkedIn des contacts clés."""
    # À enrichir avec Unipile API
    pass


def veille_web_generique():
    """Recherche générique de nouveaux cas inspirants."""
    # À enrichir avec web_search
    pass


def main():
    """Lance toutes les veilles."""
    print("=" * 60)
    print("🔍 VEILLE QUOTIDIENNE — CAS INSPIRANTS")
    print("=" * 60)

    statistiques()

    # Lancer les veilles
    veille_stade_bordelais()
    veille_label_sport_impact()
    veille_linkedin()
    veille_web_generique()

    print("\n✅ Veille terminée")
    statistiques()


if __name__ == "__main__":
    main()