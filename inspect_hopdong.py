import sys
import os
import requests
import io
import pandas as pd

url_master = "https://docs.google.com/spreadsheets/d/19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g/export?format=csv&gid=0"
response = requests.get(url_master, timeout=5)
response.encoding = 'utf-8'
df = pd.read_csv(io.StringIO(response.text), header=None, dtype=str)

for i in range(len(df.columns)):
    val = str(df.iloc[6, i]).strip()
    if 'pháp lý' in val.lower() or 'căn cứ' in val.lower() or 'hồ sơ' in val.lower():
        print(f"Col {i}: {val}")
