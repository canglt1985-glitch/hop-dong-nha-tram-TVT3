import requests
import time

lines = """DNDQ20
DNTP39
DNTP08
DNTP09
DNXL42
DNTN17 đã gia hạn 5 năm 
DNCM02
DNCM13
DNTN23
DNLK21
DNDQ40
DNTN30
DNDQ39 đã gia hạn 5 năm 
DNTP54 đã gia hạn 5 năm 
DNDQ31 đã gia hạn 5 năm 
DNCM26
DNXL62
DNDQ60
DNLK40 đã gia hạn 5 năm 
DNTP01
DNTP04
DNXL16
DNXL23
DNTP07
DNLK75
DNXL21
DNTN14 đã gia hạn 5 năm 
DNXL56
DNXL37
DNITNT1
DNTN15 đã gia hạn 5 năm 
DNCM11
DNCM43
DNCM47
DNCM24
DNLK01
DNCM23
DNTN24
DNCM38
DNLK29
DNTN38
DNDQ03
DNLK71
DNLK39
DNXL68
DNDQ06
DNXL14
DNTP30
DNDQ28
DNXL41
DNCM27
DNILKH1
DNLK28
DNCM34
DNTP33
DNXL50
DNLK03""".split("\n")

url = "http://127.0.0.1:8000/progress"

for line in lines:
    line = line.strip()
    if not line:
        continue
    site_id = line.split(" ")[0].strip()
    is_gia_han = "gia hạn 5 năm" in line.lower()
    
    payload = {
        "site_id": site_id,
        "selected_template": "thanh_ly_ky_lai" if is_gia_han else "phu_luc_giam_gia",
        "status": "gia_han_5_nam" if is_gia_han else "trinh_ky_phu_luc",
        "new_contract_no": "",
        "new_contract_date": "",
        "new_price_confirmed": None,
        "progress": {
            "draft_prepared": True,
            "submitted_internal": True,
            "signed_and_stamped": False,
            "archived_doc": False
        }
    }
    
    try:
        r = requests.post(url, json=payload)
        print(f"Updated {site_id} -> {payload['status']} | Status code: {r.status_code}")
    except Exception as e:
        print(f"Failed to update {site_id}: {e}")
    time.sleep(0.5)  # To avoid spamming Google Sheets API too fast

print("Batch update complete!")
