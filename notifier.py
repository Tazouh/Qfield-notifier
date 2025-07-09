# 4) Démarrage de session et login
session = requests.Session()
resp = session.post(
    f"{BASE_URL}/auth/login",
    data={"login": EMAIL, "password": PASSWORD},
    timeout=10,
    allow_redirects=True
)

# === DEBUG HTTP 🚨
print("▶ Login URL :", resp.url)
print("▶ Login status code :", resp.status_code)
print("▶ Login headers       :", resp.headers.get("Content-Type", ""))
print("▶ Login response text :", resp.text[:200].replace("\n"," "))
print("================================================================")
# ===================================================================

resp.raise_for_status()
