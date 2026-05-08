import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=hopdong"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

for col_idx in range(45, 52):
    print(f"--- Col {col_idx} ---")
    for r in range(4, 9):
        val = str(df.iloc[r, col_idx]).strip()
        print(f"Row {r}: {val}")

