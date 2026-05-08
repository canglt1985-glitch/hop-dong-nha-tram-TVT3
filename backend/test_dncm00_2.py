import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=hopdong"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

# Find row for DNCM00
row_idx = None
for r in range(df.shape[0]):
    val = str(df.iloc[r, 1]).strip() # Assuming col 1 is site_id
    if "DNCM00" in val:
        row_idx = r
        break

if row_idx is not None:
    print(f"Row {row_idx}:")
    for col_idx in range(df.shape[1]):
        val = str(df.iloc[row_idx, col_idx]).strip()
        if "24" in val or "2.4" in val or val.startswith("24"):
            header = str(df.iloc[6, col_idx]).strip()
            print(f"MATCH: Col {col_idx} ({header}) = {val}")
