import os
import requests
from datetime import datetime, timedelta, timezone

# 1) Variables d’environnement lues dans les secrets GitHub
EMAIL        = os.getenv("QFIELD_EMAIL")            # ex. vg@compagniedestelecomsetreseaux.com
PASSWORD     = os.getenv("QFIELD_PASSWORD")         # ex. Compagnie42
WEBHOOK_URL  = os.getenv("DISCORD_WEBHOOK_URL")     # URL de ton webhook Discord
PROJECT_ID   = os.getenv("PROJECT_ID")              # ex. valentinctr/PR4-43  (organisation/slug)

# 2) Base URL QField Cloud SaaS  (avec slash final)
BASE_URL = "https://app.qfield.cloud/api/v1/"

# 3) Vérification des variables
if not all([EMAIL, PASSWORD, WEBHOOK_URL, PROJECT_ID]):
    raise SystemExit("❌ Une ou plusieurs variables d’environnement sont manquantes")

# 4) Authentification → /sessions/  (note le slash final)
session = requests.Session()
resp = session.post(
    f"{BASE_URL}sessions/",                # <- slash final obligatoire
    json={"email": EMAIL, "password": PASSWORD},
    timeout=10
)
resp.raise_for_status()

token = resp.json().get("token")
if not token:
    raise SystemExit("❌ Impossible de récupérer le token JWT")

# 5) Ajout du token Bearer pour les appels suivants
session.headers.update({"Authorization": f"Bearer {token}"})

# 6) Timestamp 'since' : 2 min en arrière (UTC conscient du fuseau)
since = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()

# 7) Récupération des changements du projet
changes_resp = session.get(
    f"{BASE_URL}projects/{PROJECT_ID}/changes",
    params={"since": since},
    timeout=10
)
changes_resp.raise_for_status()
changes = changes_resp.json().get("changes", [])

# 8) Pour chaque changement, on poste un message Discord
for c in changes:
    message = (
        f"🔔 **Changement détecté**\n"
        f"• Feature : `{c['featureId']}`\n"
        f"• Type    : {c['type']}\n"
        f"• Par     : {c['user']['name']}\n"
        f"• À       : {c['timestamp']}"
    )
    session.post(WEBHOOK_URL, json={"content": message}, timeout=5)
