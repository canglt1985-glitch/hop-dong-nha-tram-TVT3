import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=hopdong"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

for col_idx in [47, 48, 56, 58, 68]:
    val = str(df.iloc[6, col_idx]).strip()
    val2 = str(df.iloc[7, col_idx]).strip()
    print(f"Col {col_idx}: Row 6='{val}', Row 7='{val2}'")

