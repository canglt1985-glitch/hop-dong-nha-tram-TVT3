import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url_vb = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=VB1245"
response = requests.get(url_vb)
df = pd.read_csv(io.StringIO(response.text), header=None)

print("Rows 7 to 15, cols 80, 81, 82:")
for r in range(7, min(20, df.shape[0])):
    v_id = str(df.iloc[r, 1])
    val_80 = str(df.iloc[r, 80]).strip()
    val_81 = str(df.iloc[r, 81]).strip()
    val_82 = str(df.iloc[r, 82]).strip()
    print(f"ID: {v_id} | CC(80): '{val_80}' | CD(81): '{val_81}' | CE(82): '{val_82}'")

