import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=Tien_do_ho_so"
try:
    response = requests.get(url)
    df = pd.read_csv(io.StringIO(response.text), header=None)

    for r in range(df.shape[0]):
        val = str(df.iloc[r, 0]).strip()
        if "DNXL86" in val:
            print(f"Row {r} in Tien_do_ho_so:")
            for c in range(df.shape[1]):
                print(f"Col {c}: {df.iloc[r, c]}")
            break
except Exception as e:
    print(e)
