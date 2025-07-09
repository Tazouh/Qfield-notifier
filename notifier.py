import os
import time
import requests
from datetime import datetime, timedelta, timezone

# ────────────────────────────── 1. Variables d'environnement ──────────────────────────────
EMAIL        = os.getenv("QFIELD_EMAIL")           # ex. vg@compagniedestelecomsetreseaux.com
PASSWORD     = os.getenv("QFIELD_PASSWORD")        # ex. Compagnie42
WEBHOOK_URL  = os.getenv("DISCORD_WEBHOOK_URL")    # URL complète du webhook Discord
PROJECT_ID   = os.getenv("PROJECT_ID")             # ex. valentinctr/PR4-43  (organisation/slug)

BASE_URL = "https://app.qfield.cloud"              # pas de slash final ici

if not all([EMAIL, PASSWORD, WEBHOOK_URL, PROJECT_ID]):
    raise SystemExit("❌ Variable d’environnement manquante.")

# ────────────────────────────── 2. Fonction de connexion ──────────────────────────────────
def login() -> requests.Session:
    """Retourne une session authentifiée sur QField Cloud SaaS."""
    s = requests.Session()
    print("🔑 Connexion…")
    r = s.post(
        f"{BASE_URL}/auth/login",
        data={"login": EMAIL, "password": PASSWORD},
        timeout=10,
        allow_redirects=True    # suit la redirection après login
    )
    r.raise_for_status()
    print("✅ Session ouverte.")
    return s

session = login()  # Première authentification

# ────────────────────────────── 3. Boucle de polling ──────────────────────────────────────
last_check = datetime.now(timezone.utc) - timedelta(seconds=45)  # premier since rétroactif

while True:
    try:
        since_iso = last_check.isoformat()
        url = f"{BASE_URL}/api/v1/projects/{PROJECT_ID}/changes"
        resp = session.get(url, params={"since": since_iso}, timeout=10)

        # Si la session a expiré → on se relog et on réessaie au prochain tour
        if resp.status_code == 401:
            print("🔒 Session expirée – reconnexion…")
            session = login()
            time.sleep(5)
            continue

        resp.raise_for_status()
        changes = resp.json().get("changes", [])

        # Envoi sur Discord pour chaque changement détecté
        for change in changes:
            msg = (
                f"🔔 **Changement détecté**\n"
                f"• Feature : `{change['featureId']}`\n"
                f"• Type    : {change['type']}\n"
                f"• Par     : {change['user']['name']}\n"
                f"• À       : {change['timestamp']}"
            )
            requests.post(WEBHOOK_URL, json={"content": msg}, timeout=5)

        # Met à jour le curseur temporel
        if changes:
            last_check = datetime.fromisoformat(changes[-1]["timestamp"])
        else:
            last_check = datetime.now(timezone.utc)  # rien de nouveau : on repart de maintenant

    except Exception as err:
        # Affiche l’erreur et réessaie au cycle suivant
        print("⚠️", err)

    time.sleep(30)  # Intervalle de polling (30 s)
