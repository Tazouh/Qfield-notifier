import os, requests
from datetime import datetime, timedelta
from qfieldcloud_sdk.sdk import Client

# 1) Lecture des variables d’environnement
EMAIL       = os.getenv("QFIELD_EMAIL")
PASSWORD    = os.getenv("QFIELD_PASSWORD")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")

# 2) PROJECT_ID codé en dur (organisation/slug)
PROJECT_ID  = "valentinctr/PR4-43"

# 3) Base URL avec slash final
BASE_URL    = "https://app.qfield.cloud/api/v1/"

# 4) Vérification
if not all([EMAIL, PASSWORD, WEBHOOK_URL, PROJECT_ID]):
    raise SystemExit("❌ Il manque une variable d’environnement")

# 5) Authentification via le SDK
client = Client(url=BASE_URL)
client.login(EMAIL, PASSWORD)
session = client.session

# 6) On récupère les changements des 2 dernières minutes
since = (datetime.utcnow() - timedelta(minutes=2)).isoformat()
resp = session.get(
    f"{BASE_URL}projects/{PROJECT_ID}/changes",
    params={"since": since},
    timeout=10
)
resp.raise_for_status()
changes = resp.json().get("changes", [])

# 7) Envoi sur Discord
for c in changes:
    content = (
        f"🔔 **Changement détecté**\n"
        f"• Feature : `{c['featureId']}`\n"
        f"• Type    : {c['type']}\n"
        f"• Par     : {c['user']['name']}\n"
        f"• À       : {c['timestamp']}"
    )
    session.post(WEBHOOK_URL, json={"content": content}, timeout=5)
