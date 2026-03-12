import json
import re
import unicodedata

with open('uploaded_urls.json', 'r', encoding='utf-8') as f:
    urls = json.load(f)

with open('katalogus.html', 'r', encoding='utf-8') as f:
    html = f.read()

# Normalize HTML to NFC for reliable matching
html = unicodedata.normalize('NFC', html)

for key, url in urls.items():
    # Normalize key to NFC
    key_nfc = unicodedata.normalize('NFC', key)
    
    # Safely split
    if 'Termékek/' in key_nfc:
        relative_part = key_nfc.split('Termékek/', 1)[1]
    elif 'Termékek/' in key_nfc:
        relative_part = key_nfc.split('Termékek/', 1)[1]
    else:
        continue
        
    pattern = r"['\"].*?" + re.escape(relative_part) + r"['\"]"
    
    def replacer(match):
        return f"'{url}'"
        
    html = re.sub(pattern, replacer, html)

with open('katalogus.html', 'w', encoding='utf-8') as f:
    f.write(html)
    
print("Updated katalogus.html successfully.")
