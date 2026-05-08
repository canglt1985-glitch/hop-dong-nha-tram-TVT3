import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=hopdong"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

for col_idx in range(47, 69):
    val4 = str(df.iloc[4, col_idx]).strip()
    val5 = str(df.iloc[5, col_idx]).strip()
    val6 = str(df.iloc[6, col_idx]).strip()
    if pd.notna(val5) and val5 != 'nan':
        print(f"Col {col_idx}: Row 5='{val5}', Row 6='{val6}'")

