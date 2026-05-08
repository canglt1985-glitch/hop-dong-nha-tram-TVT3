import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=VB1245"
response = requests.get(url)
df_vb = pd.read_csv(io.StringIO(response.text), header=None)

vb_map = {}
for r in range(6, df_vb.shape[0]):
    row = df_vb.iloc[r]
    if len(row) < 3: continue
    
    site_id_val = str(row[1]).strip()
    if not site_id_val or site_id_val == 'nan': continue
    
    val_80 = str(row[80]).strip() if pd.notna(row[80]) else ""
    val_81 = str(row[81]).strip() if pd.notna(row[81]) else ""
    val_82 = str(row[82]).strip() if pd.notna(row[82]) else ""
    
    has_agreed = False
    if val_80.lower() == 'x' or (val_81 and val_81 not in ['-', 'nan']) or (val_82 and val_82 not in ['-', 'nan']):
        has_agreed = True

    if site_id_val == "DNXL86":
        print(f"DNXL86: {val_80}, {val_81}, {val_82} -> {has_agreed}")

