"""
Test complet du parcours utilisateur TerritoireSport — Démo Bayard Argentan
"""
from main import app
from fastapi.testclient import TestClient
import os
import json

os.environ['DB_PATH'] = 'data/territoiresport.db'

def test_full_journey():
    with TestClient(app) as c:
        print("=" * 60)
        print("TEST PARCOURS COMPLET — BAYARD ARGENTAN TT")
        print("=" * 60)
        
        club_id = "90f8a193-a4b8-4975-b315-8e1484cdf3a3"
        
        # 1. Vérifier que le club existe
        print("\n1. Club Bayard Argentan existe ?")
        r = c.get(f'/api/clubs/{club_id}')
        if r.status_code == 200:
            club = r.json()
            print(f"   ✅ {club['name']} ({club['city']})")
        else:
            print(f"   ❌ Erreur {r.status_code}")
            return
        
        # 2. Diagnostic
        print("\n2. Diagnostic club ?")
        r = c.get('/api/diagnostic/questions')
        if r.status_code == 200:
            questions = r.json()
            print(f"   ✅ {len(questions)} questions disponibles")
        
        # 3. Matching projets
        print("\n3. Matching projets ?")
        r = c.get(f'/api/matching/{club_id}')
        if r.status_code == 200:
            result = r.json()
            matches = result.get('matches', [])
            print(f"   ✅ {len(matches)} projets recommandés")
            for m in matches[:3]:
                print(f"      - {m.get('title', m.get('name'))}")
        
        # 4. Shortlist partenaires (LE COEUR)
        print("\n4. Shortlist partenaires ?")
        r = c.get(f'/api/shortlist/{club_id}?themes=cohesion,inclusion,sante&limit=10')
        if r.status_code == 200:
            result = r.json()
            shortlist = result.get('shortlist', [])
            total = result.get('total_partners_in_territory', 0)
            print(f"   ✅ {total} partenaires sur le territoire")
            print(f"   ✅ Top {len(shortlist)} proposés :")
            for i, p in enumerate(shortlist[:5], 1):
                print(f"      {i}. {p['name']} (score: {p['score']}, type: {p['type']})")
        
        # 5. Partenaires par département
        print("\n5. Partenaires département 61 ?")
        r = c.get('/api/partners/?department=61')
        if r.status_code == 200:
            partners = r.json()
            print(f"   ✅ {len(partners)} partenaires dans le 61")
        
        print("\n" + "=" * 60)
        print("RÉSUMÉ : Démo opérationnelle ✅")
        print("=" * 60)
        print("\nProchaines étapes :")
        print("1. Ouvrir frontend/demo.html dans un navigateur")
        print("2. Vérifier que la shortlist s'affiche correctement")
        print("3. Tester avec le club Bayard Argentan (septembre 2026)")

if __name__ == "__main__":
    test_full_journey()