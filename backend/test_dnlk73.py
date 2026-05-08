import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=VB1245"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

for r in range(df.shape[0]):
    val = str(df.iloc[r, 1]).strip()
    if "DNLK73" in val:
        val_31 = str(df.iloc[r, 31]).strip()
        val_96 = str(df.iloc[r, 96]).strip()
        print(f"Col 31 (Đàm phán đạt/không đạt): '{val_31}'")
        print(f"Col 96 (Đạt/Không đạt): '{val_96}'")
        break
