import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=VB1245"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

for col_idx in range(40, 65):
    h4 = str(df.iloc[4, col_idx]).strip()
    h5 = str(df.iloc[5, col_idx]).strip()
    h6 = str(df.iloc[6, col_idx]).strip()
    print(f"Col {col_idx}: Row4: {h4} | Row5: {h5} | Row6: {h6}")
