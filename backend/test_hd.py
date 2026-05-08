import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=hopdong"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

keywords = ["Mặt bằng-QĐ", "phòng máy", "Bệ móng tủ", "Bệ Shelter", "Phòng MFĐ", "cột anten mặt đất", "Tiếp đất", "Giảm trừ dùng chung"]

for col_idx in range(df.shape[1]):
    col_texts = []
    for row_idx in range(10):
        val = str(df.iloc[row_idx, col_idx]).strip()
        if pd.notna(val) and val != 'nan' and val:
            col_texts.append(val)
    full_col_text = " | ".join(col_texts).lower()
    
    for kw in keywords:
        if kw.lower() in full_col_text:
            print(f"Col {col_idx}: {full_col_text}")
            break

