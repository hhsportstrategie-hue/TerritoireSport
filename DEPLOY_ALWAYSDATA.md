# Déploiement Alwaysdata — TerritoireSport

## Pourquoi Alwaysdata ?

- **Gratuit à vie** (free tier, sans CB)
- **SQLite persistant** (volume disque)
- **HTTPS automatique** (Let's Encrypt)
- **Domaine custom possible** (gratuit)
- **Always-on** (pas de sleep)
- **Hébergeur français** (sérieux)

## Limites free tier

- 256 MB RAM
- 1 GB disk
- Suffisant pour TerritoireSport MVP

## Étapes de déploiement

### 1. Créer un compte Alwaysdata

1. Aller sur https://www.alwaysdata.com/en/
2. Cliquer "Sign up"
3. Remplir email + mot de passe
4. Confirmer email
5. **Pas de carte bancaire requise**

### 2. Préparer le code

Le code est déjà préparé avec :
- ✅ CORS middleware
- ✅ Healthcheck (`/health`)
- ✅ Seed automatique au démarrage
- ✅ Script `deploy_alwaysdata.sh`

### 3. Upload du code

**Option A — Via SSH (recommandé)**

```bash
# Depuis ton Mac
ssh herve@ssh-youraccount.alwaysdata.net
# Mot de passe : celui du compte

# Créer le répertoire
mkdir -p ~/territoiresport
cd ~/territoiresport

# Upload via SCP (depuis ton Mac)
scp -r ./* herve@ssh-youraccount.alwaysdata.net:~/territoiresport/
```

**Option B — Via FTP/SFTP**

- Host : `ftp-youraccount.alwaysdata.net`
- User : `herve`
- Password : celui du compte
- Upload dans `~/territoiresport/`

### 4. Configurer le site Alwaysdata

Dans le panel Alwaysdata :

1. **Web > Sites > Add a site**
2. **Type** : Python
3. **Address** : `territoiresport.alwaysdata.net` (ou ton domaine custom)
4. **Path** : `~/territoiresport`
5. **Command** : `uvicorn main:app --host 0.0.0.0 --port $PORT`
6. **Python version** : 3.11

### 5. Variables d'environnement

Dans **Environment > Variables** :

```
DB_PATH=/home/herve/territoiresport/data/territoiresport.db
ENV=production
ALLOWED_ORIGINS=https://territoiresport.alwaysdata.net
PORT=8000
LOG_LEVEL=INFO
```

### 6. Installer les dépendances

**Via SSH** :

```bash
cd ~/territoiresport
pip install --user -r requirements.txt
```

### 7. Initialiser la base de données

**Via SSH** :

```bash
cd ~/territoiresport
python3 -c "import asyncio; from main import init_db; asyncio.run(init_db())"
python3 scripts/seed_db.py
```

### 8. Redémarrer le site

Dans le panel Alwaysdata :
- **Web > Sites > territoiresport > Restart**

### 9. Tester

- URL : `https://territoiresport.alwaysdata.net`
- Healthcheck : `https://territoiresport.alwaysdata.net/health`

## Domaine custom (optionnel)

### Acheter un domaine

- OVH : https://www.ovh.com/ (12 €/an pour .fr)
- Gandi : https://www.gandi.net/

### Configurer DNS

Dans le panel du registrar :
- Type : `CNAME`
- Host : `territoiresport`
- Value : `territoiresport.alwaysdata.net`

### Configurer Alwaysdata

Dans **Web > Sites > Edit** :
- Address : `territoiresport.fr`
- Alwaysdata configure HTTPS automatiquement

## Mise à jour du code

```bash
# Via SSH
cd ~/territoiresport
git pull  # si tu as configuré Git
# ou upload via SCP

# Redémarrer le site
# Panel Alwaysdata > Web > Sites > Restart
```

## Monitoring

- **Logs** : Panel Alwaysdata > Logs
- **Métriques** : Panel Alwaysdata > Statistics
- **Healthcheck** : `https://ton-url/health`

## Support

- Documentation : https://help.alwaysdata.com/en/
- Email : support@alwaysdata.com
- Forum : https://forum.alwaysdata.com/

## Coût

- **Maintenant** : 0 €/mois (free tier)
- **Plus tard** : 5 €/mois (si upgrade vers Plus)
- **Domaine custom** : 12 €/an (optionnel)