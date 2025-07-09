import time
from datetime import datetime, timedelta, timezone
from qfieldcloud_sdk.sdk import Client

# 1) Identifiants QField Cloud
LOGIN    = "valentinctr"       # ton nom d’utilisateur QField Cloud
PASSWORD = "Compagnie42"       # ton mot de passe

# 2) Webhook Discord
WEBHOOK_URL = (
    "https://discordapp.com/api/webhooks/"
    "1389636766545477776/YOXtsHBWaBVSz4noPEoB8DJKnz8ZBiSeTvdOTNtfP3MIVKmGhaFEfxCx_FNt7BxUEqrH"
)

# 3) URL de base SaaS (note bien le slash final)
BASE_URL = "https://app.qfield.cloud/"

# 4) Connexion via le SDK (gère CSRF, cookies, redirections…)
print("🔑 Connexion au SDK QFieldCloud…")
client = Client(url=BASE_URL)
client.login(LOGIN, PASSWORD)
print("✅ Authentifié en tant que", LOGIN)

# 5) Préparation du polling
poll_interval = 30  # secondes entre chaque cycle
last_checks = {}    # map project_id → datetime

while True:
    # 6) Charger la liste des projets
    projects = client.projects.list()  # [{'id':uuid, 'name':slug, …}, …]

    # Initialiser le since pour les nouveaux projets
    now = datetime.now(timezone.utc)
    for p in projects:
        if p["id"] not in last_checks:
            last_checks[p["id"]] = now - timedelta(minutes=2)

    # 7) Pour chaque projet, récupérer & notifier les changements
    for p in projects:
        pid   = p["id"]
        name  = p["name"]
        since = last_checks[pid].isoformat()

        # Cette méthode du SDK passe par /projects/{id}/changes
        resp = client.changes.list(project_id=pid, since=since)
        changes = resp.get("changes", [])

        for c in changes:
            content = (
                f"🔔 **[{name}] Changement détecté**\n"
                f"• Feature : `{c['featureId']}`\n"
                f"• Type    : {c['type']}\n"
                f"• Par     : {c['user']['name']}\n"
                f"• À       : {c['timestamp']}"
            )
            client.http.session.post(WEBHOOK_URL, json={"content": content}, timeout=5)

        # Mettre à jour le since
        last_checks[pid] = (
            datetime.fromisoformat(changes[-1]["timestamp"])
            if changes else
            now
        )

    print(f"⏱️ Cycle terminé à {datetime.now(timezone.utc).isoformat()}, attente {poll_interval}s…")
    time.sleep(poll_interval)
