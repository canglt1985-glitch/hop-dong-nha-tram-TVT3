import pandas as pd

file_price = r'd:\Chuyen doi so\soan HD\MBF ĐNa_BC_VB 1245_BÁO CÁO NGÀY.xlsx'
df_p = pd.read_excel(file_price, sheet_name='Chi tiết thuê trạm', header=None)

# Tim dong chua DNTP09 bat ke o cot nao
mask = df_p.apply(lambda row: row.astype(str).str.contains('DNTP09', case=False).any(), axis=1)
results = df_p[mask]

with open("debug_site_find.txt", "w", encoding="utf-8") as f:
    if results.empty:
        f.write("KHONG TIM THAY DNTP09 TRONG BANG GIA!\n")
    else:
        f.write(f"TIM THAY {len(results)} DONG:\n")
        for i, row in results.iterrows():
            f.write(f"Dong {i}: {row.tolist()}\n")
