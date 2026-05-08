import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=VB1245"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

for r in range(df.shape[0]):
    val = str(df.iloc[r, 1]).strip()
    if "DNCM00" in val:
        print(f"Col 5 (Old price): {df.iloc[r, 5]}")
        print(f"Col 9 (Target MT): {df.iloc[r, 9]}")
        print(f"Col 95 (Reduced): {df.iloc[r, 95]}")
        print(f"Col 31: '{df.iloc[r, 31]}'")
        print(f"Col 96: '{df.iloc[r, 96]}'")
        break
