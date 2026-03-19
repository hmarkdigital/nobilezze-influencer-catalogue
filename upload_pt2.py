import os
import uuid
import requests
import json

SUPABASE_URL = "https://wpmjustqzuavqgxoezdz.supabase.co"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwbWp1c3RxenVhdnFneG9lemR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMwOTc3OTEsImV4cCI6MjA4ODY3Mzc5MX0.ky4rszpaCh1lxGKDv6D6H0Wtbyvmm6qjj7ml30o3Weo"
BUCKET = "products"

headers = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "image/webp"
}

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

products_meta = [
    {"file": "Termékek_pt2/1-front (18).webp",  "id": "lamarthe-body-bag",          "brand": "LaMarthe",       "name": "Body Bag",                "category": "taska",  "size": None},
    {"file": "Termékek_pt2/1-front (31).webp",  "id": "mk-hatizsak",                "brand": "Michael Kors",   "name": "Hátizsák",                "category": "taska",  "size": None},
    {"file": "Termékek_pt2/1-front (42).webp",  "id": "mk-charlotte-tote-vanilla",  "brand": "Michael Kors",   "name": "Charlotte Tote Vanilla",  "category": "taska",  "size": None},
    {"file": "Termékek_pt2/1-front (43).webp",  "id": "mk-charlotte-tote-barna",    "brand": "Michael Kors",   "name": "Charlotte Tote Barna",    "category": "taska",  "size": None},
    {"file": "Termékek_pt2/1-front (45).webp",  "id": "mk-charlotte-saffiano",      "brand": "Michael Kors",   "name": "Charlotte Saffiano",      "category": "taska",  "size": None},
    {"file": "Termékek_pt2/1-front (47).webp",  "id": "mk-feher-bag",               "brand": "Michael Kors",   "name": "Fehér Bag",               "category": "taska",  "size": None},
    {"file": "Termékek_pt2/36 2:3.webp",        "id": "yeezy-350-carbon",           "brand": "Adidas",         "name": "Yeezy 350 V2 Carbon",     "category": "cipo",   "size": "36"},
    {"file": "Termékek_pt2/38-38.5-39 .webp",   "id": "nike-af1-wheat",             "brand": "Nike",           "name": "Air Force 1 Wheat",       "category": "cipo",   "size": "38, 38.5, 39"},
    {"file": "Termékek_pt2/39-pony hair.webp",  "id": "nike-af1-pony-hair",         "brand": "Nike",           "name": "Air Force 1 Pony Hair",   "category": "cipo",   "size": "39"},
]

results = []

for meta in products_meta:
    local_path = os.path.join(BASE_DIR, meta["file"])
    if not os.path.exists(local_path):
        print(f"NOT FOUND: {local_path}")
        continue

    basename = os.path.basename(local_path)
    clean_name = f"{uuid.uuid4().hex[:8]}_{basename.replace(' ', '_').replace(':', '_')}"
    clean_name = "".join(c for c in clean_name if c.isascii())
    if not clean_name.endswith(".webp"):
        clean_name += ".webp"

    upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET}/{clean_name}"

    with open(local_path, "rb") as f:
        file_data = f.read()

    print(f"Uploading {basename} → {clean_name} ...", end=" ")
    r = requests.post(upload_url, data=file_data, headers=headers)

    if r.status_code in [200, 201] or (r.status_code == 400 and "Duplicate" in r.text):
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET}/{clean_name}"
        print(f"OK → {public_url}")
        results.append({**meta, "url": public_url})
    else:
        print(f"FAILED {r.status_code}: {r.text}")

# Save results
with open(os.path.join(BASE_DIR, "pt2_uploaded.json"), "w", encoding="utf-8") as f:
    json.dump(results, f, ensure_ascii=False, indent=2)

print(f"\n✓ {len(results)}/{len(products_meta)} uploaded. Saved to pt2_uploaded.json")
