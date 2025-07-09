# notifier_sdk.py
import os
import time
from datetime import datetime, timedelta, timezone

from qfieldcloud_sdk.sdk import Client

# ─── 1) Configuration “en clair” ─────────────────────────────────────────────
LOGIN       = "valentinctr"    # votre username QField Cloud
PASSWORD    = "Compagnie42"    # votre mot de passe QField Cloud
WEBHOOK_URL = "https://discordapp.com/api/webhooks/…"
BASE_URL    = "https://app.qfield.cloud/"  # avec slash final

# ─── 2) Connexion via le SDK ───────────────────────────────────────────────────
print("🔑 Authentification via SDK…")
client = Client(url=BASE_URL)
client.login(LOGIN, PASSWORD)  # gère formulaire HTML & CSRF
print("✅ Connecté en tant que", LOGIN)

# ─── 3) Préparer le polling ───────────────────────────────────────────────────
# On gardera en mémoire pour chaque projet son timestamp "since"
last_checks = {}
poll_interval = 30  # secondes

while True:
    # 3.1) Liste actualisée des projets
    projects = client.projects.list()  # renvoie [{'id':uuid, 'name':slug}, …]

    # initialisation du since si premier cycle
    for proj in projects:
        if proj["id"] not in last_checks:
            last_checks[proj["id"]] = datetime.now(timezone.utc) - timedelta(minutes=2)

    # 3.2) Pour chaque projet, récupérer les changements
    for proj in projects:
        pid   = proj["id"]
        name  = proj["name"]
        since = last_checks[pid].isoformat()

        # le SDK fournit une méthode changes.list()
        resp = client.changes.list(project_id=pid, since=since)
        changes = resp.get("changes", [])

        # 3.3) Poster chaque changement sur Discord
        for c in changes:
            content = (
                f"🔔 **[{name}] Changement détecté**\n"
                f"• Feature : `{c['featureId']}`\n"
                f"• Type    : {c['type']}\n"
                f"• Par     : {c['user']['name']}`\n"
                f"• À       : {c['timestamp']}"
            )
            client.http.session.post(WEBHOOK_URL, json={"content": content}, timeout=5)

        # 3.4) Mettre à jour le since
        if changes:
            last_ts = changes[-1]["timestamp"]
            last_checks[pid] = datetime.fromisoformat(last_ts)

    print(f"⏱️ Cycle terminé, attente {poll_interval}s…")
    time.sleep(poll_interval)
