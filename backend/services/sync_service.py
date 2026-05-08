import requests
import json
import threading
from typing import Dict, Optional
from datetime import datetime

def fetch_online_progress(web_app_url: str) -> Optional[Dict]:
    """Fetches the latest progress data from the Google Sheets via Apps Script Web App."""
    if not web_app_url or not web_app_url.strip():
        return None
    try:
        response = requests.get(web_app_url, timeout=5)
        if response.status_code == 200:
            online_rows = response.json()
            # Convert list of rows back to site_id dictionary
            online_dict = {}
            for row in online_rows:
                site_id = row.get("site_id")
                if site_id:
                    online_dict[site_id] = {
                        "selected_template": row.get("selected_template", "thanh_ly_ky_lai"),
                        "status": row.get("status", "dong_y"),
                        "new_contract_no": row.get("new_contract_no", ""),
                        "new_contract_date": row.get("new_contract_date", ""),
                        "new_price_confirmed": float(row["new_price_confirmed"]) if row.get("new_price_confirmed") else None,
                        "progress": {
                            "draft_prepared": row.get("draft_prepared") == "TRUE",
                            "submitted_internal": row.get("submitted_internal") == "TRUE",
                            "signed_and_stamped": row.get("signed_and_stamped") == "TRUE",
                            "archived_doc": row.get("archived_doc") == "TRUE"
                        },
                        "last_updated": row.get("last_updated", datetime.now().isoformat())
                    }
            return online_dict
    except Exception as e:
        print(f"Warning: Failed to fetch online progress from Web App: {e}")
    return None

def sync_post_to_google_sheet_async(web_app_url: str, payload: Dict):
    """Sends progress update to Google Sheets Web App in a background thread."""
    def run():
        if not web_app_url or not web_app_url.strip():
            return
        try:
            headers = {"Content-Type": "application/json"}
            requests.post(web_app_url, data=json.dumps(payload), headers=headers, timeout=10)
            print("Successfully synced progress record to Google Sheets online!")
        except Exception as e:
            print(f"Error syncing to Google Sheets: {e}")
    threading.Thread(target=run, daemon=True).start()
