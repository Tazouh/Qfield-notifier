import os, time, requests
from datetime import datetime

API_TOKEN   = os.getenv("QFIELD_API_TOKEN")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PROJECT_ID  = os.getenv("PROJECT_ID")

if not API_TOKEN or not WEBHOOK_URL or not PROJECT_ID:
    raise SystemExit("❌ Variables d'environnement manquantes")

last_check = datetime.utcnow().isoformat()

while True:
    r = requests.get(
        f"https://cloud.qfield.org/api/v1/projects/{PROJECT_ID}/changes",
        headers={"Authorization": f"Bearer {API_TOKEN}"},
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
        requests.post(WEBHOOK_URL, json={"content": msg}, timeout=5)
    if changes:
        last_check = changes[-1]["timestamp"]
    time.sleep(30)
