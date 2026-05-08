import requests

url = "http://127.0.0.1:8000/sites"
try:
    response = requests.get(url)
    if response.status_code == 200:
        sites = response.json()
        
        vt3_sites = [s for s in sites if s.get("to_vt") and "3" in s["to_vt"]]
        agreed = [s for s in vt3_sites if s.get("has_agreed_1245")]
        expired = [s for s in vt3_sites if s.get("ext_status", "").find("Cần gia hạn") != -1 or (s.get("progress_tracker") and s["progress_tracker"].get("status") == "can_thanh_ly")]
        
        print(f"Total VT3 sites: {len(vt3_sites)}")
        print(f"Agreed to reduce: {len(agreed)}")
        print(f"Expired (Need resigning): {len(expired)}")
        
        print("\n--- Checking Price Frame (Khung Giá) ---")
        out_of_frame = []
        for s in vt3_sites:
            target1 = str(s.get("dat_muc_tieu_1245") or "").lower()
            target2 = str(s.get("reached_target") or "").lower()
            
            if "không đạt" in target1 or "không đạt" in target2:
                out_of_frame.append(s["site_id"])
        
        print(f"Out of price frame: {len(out_of_frame)}")
        if out_of_frame:
            print(", ".join(out_of_frame))
            
    else:
        print(f"Failed to fetch sites, status: {response.status_code}")
except Exception as e:
    print(f"Error: {e}")
