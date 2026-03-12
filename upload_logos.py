import os
import requests
import json

SUPABASE_URL = "https://wpmjustqzuavqgxoezdz.supabase.co"
API_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6IndwbWp1c3RxenVhdnFneG9lemR6Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3NzMwOTc3OTEsImV4cCI6MjA4ODY3Mzc5MX0.ky4rszpaCh1lxGKDv6D6H0Wtbyvmm6qjj7ml30o3Weo"
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
