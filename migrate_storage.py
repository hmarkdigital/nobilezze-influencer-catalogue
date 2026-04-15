import os
import json
import re
import unicodedata
import requests
from urllib.parse import quote

# ── ÚJ SUPABASE PROJEKT ──────────────────────────────────────────────────────
NEW_URL = "https://ppjvijirnkjuktlmqagx.supabase.co"
NEW_KEY = "sb_publishable_e2ayINhTxgp6naZKv9N98w_bO36XvW1"
BUCKET   = "products"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

def to_ascii_path(path):
    """Magyar ékezetes és speciális karakterek cseréje ASCII-ra."""
    path = unicodedata.normalize('NFC', path)  # macOS NFD → NFC
    replacements = {
        'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ö': 'o', 'ő': 'o',
        'ú': 'u', 'ü': 'u', 'ű': 'u',
        'Á': 'A', 'É': 'E', 'Í': 'I', 'Ó': 'O', 'Ö': 'O', 'Ő': 'O',
        'Ú': 'U', 'Ü': 'U', 'Ű': 'U',
    }
    for hu, en in replacements.items():
        path = path.replace(hu, en)
    # Speciális karakterek: zárójeleket, kettőspontot, vesszőt, szóközt tisztítjuk
    path = path.replace(' (', '_').replace('(', '_').replace(')', '')
    path = path.replace(': ', '-').replace(':', '-')
    path = path.replace(', ', '_').replace(',', '_')
    path = path.replace(' ', '-')
    path = re.sub(r'-+', '-', path)   # dupla kötőjelek összevonása
    path = re.sub(r'_+', '_', path)   # dupla aláhúzások összevonása
    return path

headers_json = {
    "apikey":        NEW_KEY,
    "Authorization": f"Bearer {NEW_KEY}",
    "Content-Type":  "application/json",
}

# ── 1. Bucket létrehozása (ha még nincs) ─────────────────────────────────────
print("── Bucket létrehozása ──────────────────────")
r = requests.post(
    f"{NEW_URL}/storage/v1/bucket",
    headers=headers_json,
    json={"id": BUCKET, "name": BUCKET, "public": True},
)
if r.status_code in [200, 201]:
    print(f"✓ '{BUCKET}' bucket létrehozva")
elif "already exists" in r.text.lower() or r.status_code == 409:
    print(f"→ '{BUCKET}' bucket már létezik, folytatás...")
else:
    print(f"⚠ Bucket hiba {r.status_code}: {r.text}")

# ── 2. Fájlok feltöltése ──────────────────────────────────────────────────────
UPLOAD_DIRS = ["Termékek", "Termékek_pt2", "Logos"]

MIME_MAP = {
    ".webp": "image/webp",
    ".jpg":  "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png":  "image/png",
    ".svg":  "image/svg+xml",
    ".mp4":  "video/mp4",
    ".mov":  "video/quicktime",
}

url_mapping = {}   # régi_url → új_url
new_urls    = {}   # lokális_path → új_url

ok = 0
fail = 0

for upload_dir in UPLOAD_DIRS:
    dir_path = os.path.join(BASE_DIR, upload_dir)
    if not os.path.exists(dir_path):
        print(f"\n── {upload_dir} mappa nem található, kihagyva")
        continue

    print(f"\n── {upload_dir} feltöltése ──────────────────────────────────────")

    for root, dirs, files in os.walk(dir_path):
        # .DS_Store és rejtett fájlok kihagyása
        files = [f for f in files if not f.startswith(".")]
        dirs[:] = [d for d in dirs if not d.startswith(".")]

        for filename in files:
            local_path = os.path.join(root, filename)
            ext = os.path.splitext(filename)[1].lower()
            mime = MIME_MAP.get(ext, "application/octet-stream")

            # Storage path: relatív az upload_dir-hez, ASCII-ra konvertálva
            rel_path = os.path.relpath(local_path, BASE_DIR)
            storage_path = to_ascii_path(rel_path.replace("\\", "/"))

            upload_url = f"{NEW_URL}/storage/v1/object/{BUCKET}/{quote(storage_path, safe='/')}"

            with open(local_path, "rb") as f:
                file_data = f.read()

            h = {
                "apikey":        NEW_KEY,
                "Authorization": f"Bearer {NEW_KEY}",
                "Content-Type":  mime,
                "x-upsert":      "true",
            }

            r = requests.post(upload_url, data=file_data, headers=h)

            public_url = f"{NEW_URL}/storage/v1/object/public/{BUCKET}/{quote(storage_path, safe='/')}"

            if r.status_code in [200, 201]:
                print(f"  ✓ {storage_path}")
                new_urls[rel_path] = public_url
                ok += 1
            elif (r.status_code == 400 and "duplicate" in r.text.lower()) or \
                 (r.status_code == 400 and "already exists" in r.text.lower()) or \
                 (r.status_code == 400 and "row-level security" in r.text.lower()):
                print(f"  → {storage_path} (már létezik)")
                new_urls[rel_path] = public_url
                ok += 1
            else:
                print(f"  ✗ {storage_path} → {r.status_code}: {r.text[:80]}")
                fail += 1

# ── 3. URL mapping mentése ────────────────────────────────────────────────────
with open(os.path.join(BASE_DIR, "new_urls.json"), "w", encoding="utf-8") as f:
    json.dump(new_urls, f, ensure_ascii=False, indent=2)

print(f"\n── Összesítés ──────────────────────────────")
print(f"✓ Sikeres: {ok}")
print(f"✗ Sikertelen: {fail}")
print(f"→ URL-ek mentve: new_urls.json")
print(f"\nKövetkező lépés: python3 update_html_urls.py")
