"""
Letölti a HTML-ben hivatkozott összes fájlt a régi Supabase-ről,
feltölti az új Supabase-be azonos névvel, majd frissíti a HTML-t.
"""
import os
import re
import requests

OLD_BASE = "https://ppjvijirnkjuktlmqagx.supabase.co"
NEW_URL  = "https://ppjvijirnkjuktlmqagx.supabase.co"
NEW_KEY  = "sb_publishable_e2ayINhTxgp6naZKv9N98w_bO36XvW1"

BASE_DIR  = os.path.dirname(os.path.abspath(__file__))
HTML_FILE = os.path.join(BASE_DIR, "katalogus.html")
CACHE_DIR = os.path.join(BASE_DIR, "_cache")
os.makedirs(CACHE_DIR, exist_ok=True)

# ── 1. HTML beolvasása, összes régi URL összegyűjtése ────────────────────────
with open(HTML_FILE, "r", encoding="utf-8") as f:
    html = f.read()

pattern = re.compile(
    r'(https://ppjvijirnkjuktlmqagx\.supabase\.co/storage/v1/object/(?:public|sign)/([^"\'>\s]+))'
)
matches = pattern.findall(html)
unique = {m[0]: m[1] for m in matches}   # url → bucket/path
print(f"── {len(unique)} egyedi URL találva a HTML-ben ────────────────────")

url_map = {}   # régi URL → új URL

for old_url, bucket_path in unique.items():
    # bucket_path pl: "products/dafb5e34_1-front.webp" vagy "nc-hero/nc-cs-0310_v2.mp4?token=..."
    path_clean = bucket_path.split("?")[0]   # token levágása
    parts      = path_clean.split("/", 1)
    if len(parts) < 2:
        print(f"  ⚠ Nem értelmezhető path: {bucket_path}")
        continue
    bucket, obj_path = parts[0], parts[1]

    # Fájlnév cache-hez (speciális karakterek cseréje)
    cache_name = obj_path.replace("/", "_").replace(" ", "_")
    cache_path = os.path.join(CACHE_DIR, cache_name)

    # ── Letöltés (ha még nincs cache-ben) ────────────────────────────────────
    if not os.path.exists(cache_path):
        print(f"  ↓ Letöltés: {obj_path[:60]}...", end=" ")
        r = requests.get(old_url, timeout=30)
        if r.status_code == 200:
            with open(cache_path, "wb") as f:
                f.write(r.content)
            print("OK")
        else:
            print(f"HIBA {r.status_code}")
            continue
    else:
        print(f"  ✓ Cache: {obj_path[:60]}")

    # ── Bucket létrehozása (ha szükséges) ─────────────────────────────────────
    requests.post(
        f"{NEW_URL}/storage/v1/bucket",
        headers={"apikey": NEW_KEY, "Authorization": f"Bearer {NEW_KEY}",
                 "Content-Type": "application/json"},
        json={"id": bucket, "name": bucket, "public": True},
    )

    # ── Feltöltés az új Supabase-be ───────────────────────────────────────────
    ext = os.path.splitext(obj_path)[1].lower()
    mime_map = {".webp": "image/webp", ".jpg": "image/jpeg", ".jpeg": "image/jpeg",
                ".png": "image/png", ".svg": "image/svg+xml",
                ".mp4": "video/mp4", ".mov": "video/quicktime"}
    mime = mime_map.get(ext, "application/octet-stream")

    from urllib.parse import quote
    upload_url = f"{NEW_URL}/storage/v1/object/{bucket}/{quote(obj_path, safe='/')}"
    h = {"apikey": NEW_KEY, "Authorization": f"Bearer {NEW_KEY}",
         "Content-Type": mime, "x-upsert": "true"}

    with open(cache_path, "rb") as f:
        r = requests.post(upload_url, data=f.read(), headers=h)

    new_public_url = f"{NEW_URL}/storage/v1/object/public/{bucket}/{quote(obj_path, safe='/')}"

    if r.status_code in [200, 201]:
        print(f"  ↑ Feltöltve: {obj_path[:60]}")
        url_map[old_url] = new_public_url
    elif "row-level security" in r.text or "already" in r.text.lower() or "duplicate" in r.text.lower():
        print(f"  → Már létezik: {obj_path[:60]}")
        url_map[old_url] = new_public_url
    else:
        print(f"  ✗ Feltöltés hiba {r.status_code}: {r.text[:80]}")

# ── 2. HTML frissítése ────────────────────────────────────────────────────────
print(f"\n── HTML frissítése ({len(url_map)} URL csere) ─────────────────────")
updated = html
for old_url, new_url in url_map.items():
    updated = updated.replace(old_url, new_url)

with open(HTML_FILE, "w", encoding="utf-8") as f:
    f.write(updated)

remaining = len(re.findall(r'ppjvijirnkjuktlmqagx', updated))
print(f"✓ HTML mentve: katalogus.html")
print(f"{'✓ Nincs több régi URL' if remaining == 0 else f'⚠ Még {remaining} régi URL maradt'}")
