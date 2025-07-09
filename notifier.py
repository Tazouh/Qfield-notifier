import os, time, requests
from datetime import datetime

EMAIL       = os.getenv("QFIELD_EMAIL")
PASSWORD    = os.getenv("QFIELD_PASSWORD")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PROJECT_ID  = os.getenv("PROJECT_ID")
BASE_URL    = "https://app.qfield.cloud/api/v1"

if not all([EMAIL, PASSWORD, WEBHOOK_URL, PROJECT_ID]):
    raise SystemExit("❌ Variables d’environnement manquantes")

session = requests.Session()

# Authentification (form data, pas de slash d’excès)
session.post(
    f"{BASE_URL}/auth/login",
    data={"login": EMAIL, "password": PASSWORD},
    timeout=10
).raise_for_status()

last_check = datetime.utcnow().isoformat()

while True:
    # 1) Récupérer les changements depuis last_check
    r = session.get(
        f"{BASE_URL}/projects/{PROJECT_ID}/changes",
        params={"since": last_check},
        timeout=10
    )
    r.raise_for_status()
    changes = r.json().get("changes", [])

    # 2) Pour chaque changement, poster sur Discord
    for c in changes:
        msg = (
            f"🔔 **Changement détecté**\n"
            f"• Feature : `{c['featureId']}`\n"
            f"• Type    : {c['type']}\n"
            f"• Par     : {c['user']['name']}\n"
            f"• À       : {c['timestamp']}"
        )
        session.post(WEBHOOK_URL, json={"content": msg}, timeout=5)

    # 3) Mettre à jour le timestamp
    if changes:
        last_check = changes[-1]["timestamp"]

    # 4) Attendre 30 secondes
    time.sleep(30)
