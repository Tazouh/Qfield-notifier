import time
import requests
from datetime import datetime, timedelta, timezone

# ─── 1) Identifiants en clair ────────────────────────────────────────────────
LOGIN       = "valentinctr"
PASSWORD    = "Compagnie42"
WEBHOOK_URL = "https://discordapp.com/api/webhooks/…"
BASE_URL    = "https://app.qfield.cloud"  # sans slash final

# ─── 2) Connexion (une seule fois) ───────────────────────────────────────────
def login() -> requests.Session:
    s = requests.Session()
    r = s.post(
        f"{BASE_URL}/auth/login",
        data={"login": LOGIN, "password": PASSWORD},
        timeout=10,
        allow_redirects=True
    )
    r.raise_for_status()
    return s

session = login()

# ─── 3) Récupérer la liste des projets et initialiser les timestamps ────────
resp = session.get(f"{BASE_URL}/api/v1/projects/", timeout=10)
resp.raise_for_status()
projects = resp.json()  # liste de dict { "id": "...", "name": "...", ... }

# Pour chaque projet, on conserve un "since" initial 2 minutes en arrière
last_checks = {
    proj["id"]: datetime.now(timezone.utc) - timedelta(minutes=2)
    for proj in projects
}

# ─── 4) Boucle de polling ─────────────────────────────────────────────────────
while True:
    for proj in projects:
        pid = proj["id"]
        since_iso = last_checks[pid].isoformat()
        url = f"{BASE_URL}/api/v1/projects/{pid}/changes"
        r = session.get(url, params={"since": since_iso}, timeout=10)

        # si on est déconnecté, on relogne et on skip ce tour
        if r.status_code == 401:
            session = login()
            continue

        r.raise_for_status()
        changes = r.json().get("changes", [])

        # pour chaque changement, on notifie Discord
        for c in changes:
            content = (
                f"🔔 **[{proj['name']}] Changement détecté**\n"
                f"• Feature : `{c['featureId']}`\n"
                f"• Type    : {c['type']}\n"
                f"• Par     : {c['user']['name']}\n"
                f"• À       : {c['timestamp']}"
            )
            session.post(WEBHOOK_URL, json={"content": content}, timeout=5)

        # on met à jour le since pour ce projet
        if changes:
            # prend le timestamp du dernier changement retourné
            last_checks[pid] = datetime.fromisoformat(changes[-1]["timestamp"])
        else:
            # sinon avance le curseur à l'instant présent
            last_checks[pid] = datetime.now(timezone.utc)

    # pause avant le prochain cycle
    time.sleep(30)
