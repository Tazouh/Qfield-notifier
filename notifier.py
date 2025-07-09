import os, time, requests
from datetime import datetime

EMAIL       = os.getenv("QFIELD_EMAIL")
PASSWORD    = os.getenv("QFIELD_PASSWORD")
WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")
PROJECT_ID  = os.getenv("PROJECT_ID")
BASE_URL    = "https://app.qfield.cloud/api/v1"

# === DEBUG : imprime l’état des variables ================================
print("▶ QFIELD_EMAIL     :", EMAIL is not None, EMAIL or "")
print("▶ QFIELD_PASSWORD  :", PASSWORD is not None, ("*" * len(PASSWORD)) if PASSWORD else "")
print("▶ DISCORD_WEBHOOK_URL:", WEBHOOK_URL is not None, WEBHOOK_URL or "")
print("▶ PROJECT_ID       :", PROJECT_ID is not None, PROJECT_ID or "")
print("======================================================================")
# ========================================================================

if not all([EMAIL, PASSWORD, WEBHOOK_URL, PROJECT_ID]):
    raise SystemExit("❌ Il manque une variable d’environnement")
