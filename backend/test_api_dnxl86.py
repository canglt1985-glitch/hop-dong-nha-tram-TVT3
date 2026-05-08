import requests

try:
    data = requests.get("http://localhost:8000/api/sites").json()
    for site in data:
        if site["site_id"] == "DNXL86":
            import json
            print(json.dumps(site, indent=2, ensure_ascii=False))
            break
except Exception as e:
    print(e)
