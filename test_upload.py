import glob
import os
import requests
import json
import uuid

SUPABASE_URL = "https://wpmjustqzuavqgxoezdz.supabase.co"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwbWp1c3RxenVhdnFneG9lemR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMwOTc3OTEsImV4cCI6MjA4ODY3Mzc5MX0.ky4rszpaCh1lxGKDv6D6H0Wtbyvmm6qjj7ml30o3Weo"
BUCKET_NAME = "products"

headers = {
    "apikey": API_KEY,
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "image/webp"
}

with open('uploaded_urls.json', 'r', encoding='utf-8') as f:
    old_mapping = json.load(f)

# old_mapping: local_path -> broken_supabase_url

new_mapping = {}

with open('katalogus.html', 'r', encoding='utf-8') as f:
    html = f.read()

for local_path, broken_url in old_mapping.items():
    if not os.path.exists(local_path):
        print(f"File not found: {local_path}")
        continue
        
    # Generate clean name
    clean_name = f"{uuid.uuid4().hex[:8]}_{os.path.basename(local_path).replace(' ', '_')}"
    # Remove any stray non-ascii from basename
    clean_name = "".join([c for c in clean_name if c.isascii()])
    if not clean_name.endswith(".webp"):
        clean_name += ".webp"
        
    upload_url = f"{SUPABASE_URL}/storage/v1/object/{BUCKET_NAME}/{clean_name}"
    
    with open(local_path, 'rb') as f:
        file_data = f.read()
        
    print(f"Uploading {local_path} as {clean_name}...")
    r = requests.post(upload_url, data=file_data, headers=headers)
    
    if r.status_code in [200, 201, 400]:
        if r.status_code == 400 and 'Duplicate' not in r.text:
            print(f"Failed {local_path}: {r.status_code} {r.text}")
            continue
            
        public_url = f"{SUPABASE_URL}/storage/v1/object/public/{BUCKET_NAME}/{clean_name}"
        html = html.replace(broken_url, public_url)
        print(f"Replaced in html!")
    else:
        print(f"Failed {local_path}: {r.status_code} {r.text}")

with open('katalogus.html', 'w', encoding='utf-8') as f:
    f.write(html)
    
print("Updated katalogus.html successfully.")
