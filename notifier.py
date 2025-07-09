import time
import requests
from datetime import datetime, timedelta, timezone

# ─── 1) Identifiants et config (en clair pour test) ─────────────────
LOGIN       = "valentinctr"
PASSWORD    = "Compagnie42"
WEBHOOK_URL = "https://discordapp.com/api/webhooks/…"
PROJECT_ID  = "4a70a191-a077-4a71-9bcc-51c558ee8b84"  # ← l'UUID du projet
BASE_URL    = "https://app.qfield.cloud"

# ─── 2) Vérifications ────────────────────────────────────────────────
for var, name in [(LOGIN,"LOGIN"), (PASSWORD,"PASSWORD"),
                  (WEBHOOK_URL,"WEBHOOK_URL"), (PROJECT_ID,"PROJECT_ID")]:
    if not var:
        raise SystemExit(f"❌ La variable {name} est manquante")

# ─── 3) Connexion ────────────────────────────────────────────────────
session = requests.Session()
resp = session.post(
    f"{BASE_URL}/auth/login",
    data={"login": LOGIN, "password": PASSWORD},
    timeout=10,
    allow_redirects=True
)
resp.raise_for_status()

# ─── 4) Boucle de polling (30 s) ──────────────────────────────────────
while True:
    since = (datetime.now(timezone.utc) - timedelta(seconds=45)).isoformat()
    url = f"{BASE_URL}/api/v1/projects/{PROJECT_ID}/changes"
    r = session.get(url, params={"since": since}, timeout=10)

    # reconnexion si nécessaire
    if r.status_code == 401:
        session.post(
            f"{BASE_URL}/auth/login",
            data={"login": LOGIN, "password": PASSWORD},
            timeout=10,
            allow_redirects=True
        ).raise_for_status()
        time.sleep(5)
        continue

    r.raise_for_status()
    for c in r.json().get("changes", []):
        msg = (
            f"🔔 **Changement détecté**\n"
            f"• Feature : `{c['featureId']}`\n"
            f"• Type    : {c['type']}\n"
            f"• Par     : {c['user']['name']}`\n"
            f"• À       : {c['timestamp']}"
        )
        session.post(WEBHOOK_URL, json={"content": msg}, timeout=5)

    time.sleep(30)
