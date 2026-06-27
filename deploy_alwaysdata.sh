#!/bin/bash
# ── Script de déploiement Alwaysdata ──────────────────────────────
# Usage : bash deploy_alwaysdata.sh

set -e

echo "🚀 Déploiement TerritoireSport sur Alwaysdata"
echo ""

# ── 1. Vérifications préalables ──────────────────────────────────
echo "1️⃣  Vérifications..."

if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt introuvable"
    exit 1
fi

if [ ! -d "frontend" ]; then
    echo "❌ Dossier frontend/ introuvable"
    exit 1
fi

if [ ! -d "data" ]; then
    echo "❌ Dossier data/ introuvable"
    exit 1
fi

echo "   ✅ Structure OK"
echo ""

# ── 2. Installation des dépendances ───────────────────────────────
echo "2️⃣  Installation des dépendances..."
pip install --user -r requirements.txt
echo "   ✅ Dépendances installées"
echo ""

# ── 3. Initialisation DB ─────────────────────────────────────────
echo "3️⃣  Initialisation base de données..."
python3 -c "import asyncio; from main import init_db; asyncio.run(init_db())"
echo "   ✅ DB initialisée"
echo ""

# ── 4. Seed données ───────────────────────────────────────────────
echo "4️⃣  Import des données..."
python3 scripts/seed_db.py
echo "   ✅ Données importées"
echo ""

# ── 5. Test rapide ────────────────────────────────────────────────
echo "5️⃣  Test de l'application..."
python3 -c "
from fastapi.testclient import TestClient
from main import app
client = TestClient(app)
r = client.get('/health')
print(f'   Healthcheck: {r.status_code} {r.json()}')
r = client.get('/')
print(f'   Frontend: {r.status_code}')
"
echo ""

echo "🎉 Déploiement prêt !"
echo ""
echo "📋 Prochaines étapes :"
echo "   1. Configurer le site Alwaysdata :"
echo "      - Type : Python WSGI/ASGI"
echo "      - Commande : uvicorn main:app --host 0.0.0.0 --port \$PORT"
echo "      - Version Python : 3.11"
echo "   2. Ajouter les variables d'environnement (voir .env.example)"
echo "   3. Activer HTTPS (Let's Encrypt auto)"
echo "   4. Tester l'URL fournie par Alwaysdata"