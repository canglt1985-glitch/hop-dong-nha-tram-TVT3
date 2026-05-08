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
        print(f"Col 80: {df.iloc[r, 80]}")
        print(f"Col 81: {df.iloc[r, 81]}")
        print(f"Col 82: {df.iloc[r, 82]}")
        break
