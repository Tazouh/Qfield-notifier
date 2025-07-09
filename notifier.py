import os, time, requests
from datetime import datetime

# 1) Tous les paramètres viennent de l’environnement
EMAIL       = os.getenv("QFIELD_EMAIL")
PASSWORD    = os.getenv("QFIELD_PASSWORD")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PROJECT_ID  = os.getenv("PROJECT_ID")
BASE_URL    = "https://app.qfield.cloud/api/v1"

# 2) Vérification
if not all([EMAIL, PASSWORD, WEBHOOK_URL, PROJECT_ID]):
    raise SystemExit("❌ Il manque une des variables d’environnement")

# 3) Authentification (création de session)
session = requests.Session()
resp = session.post(
    f"{BASE_URL}/sessions",
    json={"login": EMAIL, "password": PASSWORD},
    timeout=10
)
resp.raise_for_status()

# 4) Boucle de polling
last_check = datetime.utcnow().isoformat()
while True:
    r = session.get(
        f"{BASE_URL}/projects/{PROJECT_ID}/changes",
        params={"since": last_check},
        timeout=10
    )
    r.raise_for_status()
    changes = r.json().get("changes", [])

    for c in changes:
        msg = (
            f"🔔 **Changement détecté**\n"
            f"• Feature : `{c['featureId']}`\n"
            f"• Type    : {c['type']}\n"
            f"• Par     : {c['user']['name']}\n"
            f"• À       : {c['timestamp']}"
        )
        session.post(WEBHOOK_URL, json={"content": msg}, timeout=5)

    if changes:
        last_check = changes[-1]["timestamp"]
    time.sleep(30)
