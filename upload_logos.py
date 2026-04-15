import os
import requests
import json

SUPABASE_URL = "https://ppjvijirnkjuktlmqagx.supabase.co"
API_KEY = "sb_publishable_e2ayINhTxgp6naZKv9N98w_bO36XvW1"
BUCKET_NAME = "products"

headers = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}"
}

logos = ["Logos/nc-logo-black.svg", "Logos/nc-logo-white.svg"]
urls = {}

for logo in logos:
    basename = os.path.basename(logo)
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{basename}"
    
    with open(logo, 'rb') as f:
        file_data = f.read()
        
    print(f"Uploading {logo}...")
    headers["Content-Type"] = "image/svg+xml"
    r = requests.post(upload_url, data=file_data, headers=headers)
    
    url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{basename}"
    urls[logo] = url

with open('katalogus.html', 'r', encoding='utf-8') as f:
    html = f.read()

for local, remote in urls.items():
    html = html.replace(local, remote)

with open('katalogus.html', 'w', encoding='utf-8') as f:
    f.write(html)

print("Logos uploaded and HTML updated.")
