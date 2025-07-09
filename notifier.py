import os, requests
from datetime import datetime, timedelta

# Lecture des variables d’environnement
EMAIL       = os.getenv("QFIELD_EMAIL")
PASSWORD    = os.getenv("QFIELD_PASSWORD")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PROJECT_ID  = os.getenv("PROJECT_ID")
BASE_URL    = "https://app.qfield.cloud/api/v1"

# Vérification
if not all([EMAIL, PASSWORD, WEBHOOK_URL, PROJECT_ID]):
    raise SystemExit("❌ Il manque une variable d’environnement")

# Authentification
session = requests.Session()
session.post(
    f"{BASE_URL}/sessions",
    json={"login": EMAIL, "password": PASSWORD},
    timeout=10
).raise_for_status()

# On récupère les changements des 2 dernières minutes
since = (datetime.utcnow() - timedelta(minutes=2)).isoformat()
r = session.get(
    f"{BASE_URL}/projects/{PROJECT_ID}/changes",
    params={"since": since},
    timeout=10
)
r.raise_for_status()
changes = r.json().get("changes", [])

# Notification Discord pour chaque changement
for c in changes:
    msg = (
        f"🔔 **Changement détecté**\n"
        f"• Feature : `{c['featureId']}`\n"
        f"• Type    : {c['type']}\n"
        f"• Par     : {c['user']['name']}\n"
        f"• À       : {c['timestamp']}"
    )
    session.post(WEBHOOK_URL, json={"content": msg}, timeout=5)
