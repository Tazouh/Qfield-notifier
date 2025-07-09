import time
import requests
from datetime import datetime, timedelta, timezone

# ─── 1) Variables d’environnement (hard-codées pour test) ────────────────────────
LOGIN       = "valentinctr"  # ton username QField Cloud
PASSWORD    = "Compagnie42"  # ton mot de passe
WEBHOOK_URL = "https://discordapp.com/api/webhooks/…"
PROJECT_ID  = "valentinctr/PR4-43"  # organisation/slug exact
BASE_URL    = "https://app.qfield.cloud"  # sans slash final

# ─── 2) Vérification ────────────────────────────────────────
for var, name in [
    (LOGIN, "LOGIN"),
    (PASSWORD, "PASSWORD"),
    (WEBHOOK_URL, "DISCORD_WEBHOOK_URL"),
    (PROJECT_ID, "PROJECT_ID")
]:
    if not var:
        raise SystemExit(f"❌ La variable {name} est manquante")

# ─── 3) Authentification via /auth/login ───────────────────────────────
session = requests.Session()
resp = session.post(
    f"{BASE_URL}/auth/login",
    data={"login": LOGIN, "password": PASSWORD},
    timeout=10,
    allow_redirects=True
)
resp.raise_for_status()  # Doit renvoyer 200 OK

# ─── 4) Calcul du “since” (2 min en arrière) ─────────────────────────────
since = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()

# ─── 5) Récupération des changements ─────────────────────────────────────
r = session.get(
    f"{BASE_URL}/api/v1/projects/{PROJECT_ID}/changes",
    params={"since": since},
    timeout=10
)
r.raise_for_status()
changes = r.json().get("changes", [])

# ─── 6) Envoi sur Discord ────────────────────────────────────────────────
for c in changes:
    msg = (
        f"🔔 **Changement détecté**\n"
        f"• Feature : `{c['featureId']}`\n"
        f"• Type    : {c['type']}\n"
        f"• Par     : {c['user']['name']}`\n"
        f"• À       : {c['timestamp']}"
    )
    requests.post(WEBHOOK_URL, json={"content": msg}, timeout=5)

# ─── 7) Pause de 30 s (utile en local ou sur Railway) ────────────────────
time.sleep(30)
