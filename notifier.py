import os, requests
from datetime import datetime, timedelta

# --- 1) Variables d'environnement -----------------------
EMAIL       = os.getenv("QFIELD_EMAIL")
PASSWORD    = os.getenv("QFIELD_PASSWORD")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PROJECT_ID  = "valentinctr/PR4-43"   # ton organisation/slug

# --- 2) Base URL (sans slash final) --------------------
BASE_URL    = "https://app.qfield.cloud/api/v1"

# --- 3) Vérification -----------------------------
if not all([EMAIL, PASSWORD, WEBHOOK_URL, PROJECT_ID]):
    raise SystemExit("❌ Une variable d'environnement est manquante")

# --- 4) Démarrage de session et login ------------
session = requests.Session()
resp = session.post(
    f"{BASE_URL}/auth/login",      # note : pas de slash en trop
    data={"login": EMAIL, "password": PASSWORD},
    timeout=10
)
resp.raise_for_status()  # doit renvoyer 200 OK

# --- 5) Calcul du 'since' : 2 minutes en arrière -----
since = (datetime.utcnow() - timedelta(minutes=2)).isoformat()

# --- 6) Récupération des changements ---------------
resp = session.get(
    f"{BASE_URL}/projects/{PROJECT_ID}/changes",
    params={"since": since},
    timeout=10
)
resp.raise_for_status()
changes = resp.json().get("changes", [])

# --- 7) Envoi vers Discord ------------------------
for c in changes:
    payload = {
        "content": (
            f"🔔 **Changement détecté**\n"
            f"• Feature : `{c['featureId']}`\n"
            f"• Type    : {c['type']}\n"
            f"• Par     : {c['user']['name']}\n"
            f"• À       : {c['timestamp']}"
        )
    }
    session.post(WEBHOOK_URL, json=payload, timeout=5)
