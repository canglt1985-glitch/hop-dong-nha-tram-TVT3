import requests
import pandas as pd
import io

spreadsheet_id = "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g"
url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=VB1245"
response = requests.get(url)
df = pd.read_csv(io.StringIO(response.text), header=None)

# Find row for DNCM00
row_idx = None
for r in range(df.shape[0]):
    val = str(df.iloc[r, 1]).strip() # Assuming col 1 is site_id
    if "DNCM00" in val:
        row_idx = r
        break

if row_idx is not None:
    print(f"Row DNCM00 is {row_idx}")
    for col_idx in range(df.shape[1]):
        col_texts = []
        for r in range(5, 8):
            val = str(df.iloc[r, col_idx]).strip()
            if pd.notna(val) and val != 'nan':
                col_texts.append(val)
        
        val_dncm00 = str(df.iloc[row_idx, col_idx]).strip()
        
        # Only print if there is some header or value
        if col_texts or (pd.notna(val_dncm00) and val_dncm00 != 'nan' and val_dncm00 != '-'):
            print(f"Col {col_idx}: {' | '.join(col_texts)} -> {val_dncm00}")

