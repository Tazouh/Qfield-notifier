import os
import time
import requests
from datetime import datetime, timedelta, timezone

# ─── 1) Variables d’environnement ────────────────────────────
EMAIL       = os.getenv("QFIELD_EMAIL")
PASSWORD    = os.getenv("QFIELD_PASSWORD")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
#PROJECT_ID  = os.getenv("PROJECT_ID")
PROJECT_ID  = "valentinctr/PR4-43"   # Hardcoded pour tester
BASE_URL    = "https://app.qfield.cloud"


# ─── 2) Vérification ────────────────────────────────────────
for var, name in [(EMAIL,"QFIELD_EMAIL"), (PASSWORD,"QFIELD_PASSWORD"),
                  (WEBHOOK_URL,"DISCORD_WEBHOOK_URL"), (PROJECT_ID,"PROJECT_ID")]:
    if not var:
        raise SystemExit(f"❌ La variable {name} est manquante")

# ─── 3) Login avec debug HTTP ───────────────────────────────
session = requests.Session()
resp = session.post(
    f"{BASE_URL}/auth/login",
    data={"login": EMAIL, "password": PASSWORD},
    timeout=10,
    allow_redirects=True
)

# Debug HTTP
print("▶ Login URL           :", resp.url)
print("▶ Login status code   :", resp.status_code)
print("▶ Login Content-Type  :", resp.headers.get("Content-Type", ""))
print("▶ Login response (200 chars):", resp.text[:200].replace("\n"," "))
print("────────────────────────────────────────────────────────────")

resp.raise_for_status()

# ─── 4) On calcule “since” ─────────────────────────────────
since = (datetime.now(timezone.utc) - timedelta(minutes=2)).isoformat()

# ─── 5) Récupération des changements ────────────────────────
r2 = session.get(
    f"{BASE_URL}/api/v1/projects/{PROJECT_ID}/changes",
    params={"since": since},
    timeout=10
)

# Debug changes
print("▶ Changes URL        :", r2.url)
print("▶ Changes status code:", r2.status_code)
print("▶ Changes Content-Type:", r2.headers.get("Content-Type",""))
print("▶ Changes response (200 chars):", r2.text[:200].replace("\n"," "))
print("────────────────────────────────────────────────────────────")

r2.raise_for_status()
changes = r2.json().get("changes", [])

# ─── 6) Envoi sur Discord ───────────────────────────────────
for c in changes:
    msg = (
        f"🔔 **Changement détecté**\n"
        f"• Feature : `{c['featureId']}`\n"
        f"• Type    : {c['type']}\n"
        f"• Par     : {c['user']['name']}`\n"
        f"• À       : {c['timestamp']}"
    )
    requests.post(WEBHOOK_URL, json={"content": msg}, timeout=5)
