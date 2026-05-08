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
        print(f"Row {r} found! {df.iloc[r, 1]}")
