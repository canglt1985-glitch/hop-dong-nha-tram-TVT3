import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=VB1245"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

for r in range(df.shape[0]):
    val = str(df.iloc[r, 1]).strip()
    if "DNXL86" in val:
        val_80 = str(df.iloc[r, 80]).strip() if pd.notna(df.iloc[r, 80]) else ""
        val_81 = str(df.iloc[r, 81]).strip() if pd.notna(df.iloc[r, 81]) else ""
        val_82 = str(df.iloc[r, 82]).strip() if pd.notna(df.iloc[r, 82]) else ""
        has_agreed = False
        if val_80.lower() == 'x' or (val_81 and val_81 not in ['-', 'nan']) or (val_82 and val_82 not in ['-', 'nan']):
            has_agreed = True
        print(f"val_80: '{val_80}'")
        print(f"val_81: '{val_81}'")
        print(f"val_82: '{val_82}'")
        print(f"has_agreed: {has_agreed}")
        break
