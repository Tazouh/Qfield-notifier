import os, requests
from datetime import datetime, timedelta

# 1) Variables d'environnement
EMAIL       = os.getenv("QFIELD_EMAIL")
PASSWORD    = os.getenv("QFIELD_PASSWORD")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PROJECT_ID  = os.getenv("PROJECT_ID")  # organisation/slug, ex. "valentinctr/PR4-43"

# 2) Base URL
BASE_URL    = "https://app.qfield.cloud/api/v1/"

# 3) Vérification
if not all([EMAIL, PASSWORD, WEBHOOK_URL, PROJECT_ID]):
    raise SystemExit("❌ Une variable d'environnement est manquante")

# 4) Authentification via /sessions ⇢ on récupère un token JWT
session = requests.Session()
r = session.post(
    f"{BASE_URL}sessions",
    json={"email": EMAIL, "password": PASSWORD},
    timeout=10
)
r.raise_for_status()
token = r.json().get("token")
if not token:
    raise SystemExit("❌ Impossible de récupérer le token API")

# 5) On passe le token en header Bearer pour tous les appels suivants
session.headers.update({"Authorization": f"Bearer {token}"})

# 6) Calcul du 'since' : 2 minutes en arrière
since = (datetime.utcnow() - timedelta(minutes=2)).isoformat()

# 7) Récupération des changements
r = session.get(
    f"{BASE_URL}projects/{PROJECT_ID}/changes",
    params={"since": since},
    timeout=10
)
r.raise_for_status()
changes = r.json().get("changes", [])

# 8) Envoi sur Discord
for c in changes:
    session.post(
        WEBHOOK_URL,
        json={"content":(
            f"🔔 **Changement détecté**\n"
            f"• Feature : `{c['featureId']}`\n"
            f"• Type    : {c['type']}\n"
            f"• Par     : {c['user']['name']}\n"
            f"• À       : {c['timestamp']}"
        )},
        timeout=5
    )
