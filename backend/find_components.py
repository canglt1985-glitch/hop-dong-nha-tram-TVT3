import pandas as pd
import sys
import io

sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

PRICE_EXCEL = r'd:\Chuyen doi so\soan HD\MBF ĐNa_BC_VB 1245_BÁO CÁO NGÀY.xlsx'

def find_components(site_id):
    df_price = pd.read_excel(PRICE_EXCEL, sheet_name='Chi tiết thuê trạm', header=None)
    row = df_price[df_price.iloc[:, 1].astype(str).str.contains(site_id, na=False)]
    
    if len(row) > 0:
        p_row = row.iloc[0]
        print(f"Components for {site_id}:")
        for i, val in enumerate(p_row):
            if pd.notna(val) and isinstance(val, (int, float)) and val > 0:
                print(f"Col {i}: {val}")

if __name__ == "__main__":
    find_components("DNCM01")
