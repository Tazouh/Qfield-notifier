# notifier.py
import os
import requests
from datetime import datetime, timedelta
from qfieldcloud_sdk.sdk import Client

# 1) Lecture des variables d’environnement (remplies via GitHub Secrets)
EMAIL       = os.getenv("QFIELD_EMAIL")
PASSWORD    = os.getenv("QFIELD_PASSWORD")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PROJECT_ID  = os.getenv("PROJECT_ID")
BASE_URL    = "https://app.qfield.cloud/api/v1"

if not all([EMAIL, PASSWORD, WEBHOOK_URL, PROJECT_ID]):
    raise SystemExit("❌ Il manque une variable d’environnement")

# 2) Authentification via le SDK
client = Client(url=BASE_URL)
client.login(EMAIL, PASSWORD)

# On récupère la session configurée
session = client.session

# 3) Calcul du timestamp “since” : 2 minutes en arrière
since = (datetime.utcnow() - timedelta(minutes=2)).isoformat()

# 4) Appel au endpoint des changements
resp = session.get(
    f"{BASE_URL}/projects/{PROJECT_ID}/changes",
    params={"since": since},
    timeout=10
)
resp.raise_for_status()
changes = resp.json().get("changes", [])

# 5) Pour chaque changement, on poste sur Discord
for c in changes:
    content = (
        f"🔔 **Changement détecté**\n"
        f"• Feature : `{c['featureId']}`\n"
        f"• Type    : {c['type']}\n"
        f"• Par     : {c['user']['name']}\n"
        f"• À       : {c['timestamp']}"
    )
    requests.post(WEBHOOK_URL, json={"content": content}, timeout=5)
