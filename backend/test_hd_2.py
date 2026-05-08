import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=hopdong"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

for col_idx in range(45, 75):
    val = str(df.iloc[6, col_idx]).strip()
    val2 = str(df.iloc[7, col_idx]).strip()
    if pd.notna(val) and val != 'nan':
        print(f"Col {col_idx}: Row 6='{val}', Row 7='{val2}'")

