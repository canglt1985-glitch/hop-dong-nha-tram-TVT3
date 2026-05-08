import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=hopdong"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

for col_idx in range(45, 75):
    col_texts = []
    for row_idx in range(8):
        val = str(df.iloc[row_idx, col_idx]).strip()
        if pd.notna(val) and val != 'nan' and val:
            col_texts.append(val)
    if col_texts:
        print(f"Col {col_idx}: {' | '.join(col_texts)}")

