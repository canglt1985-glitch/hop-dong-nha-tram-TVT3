import pandas as pd
from typing import Dict

def parse_numeric_value(val) -> float:
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip()
    if not val_str:
        return 0.0
    try:
        # Remove common currency symbols, spaces
        val_str = val_str.replace("đ", "").replace("VND", "").replace(" ", "").replace("\xa0", "").strip()
        # Handle Vietnamese formatting where '.' is thousands and ',' is decimal
        if "." in val_str and "," in val_str:
            val_str = val_str.replace(".", "").replace(",", ".")
        elif "." in val_str:
            parts = val_str.split(".")
            if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3):
                val_str = val_str.replace(".", "")
            else:
                pass
        elif "," in val_str:
            val_str = val_str.replace(",", ".")
        return float(val_str)
    except Exception:
        return 0.0

def find_header_indices(df: pd.DataFrame) -> Dict[str, int]:
    """
    Scans Row index 6 (Row 7 in spreadsheet) for exact and fuzzy matching header terms
    to prevent index shifting issues between Google Sheets and local Excel.
    """
    headers = [str(x).strip().lower() if pd.notna(x) else "" for x in df.iloc[6]]
    
    # Defaults based on standard Excel layout
    mapping = {
        "site_id": 1,          # 'Mã trạm'
        "owner": 16,           # 'Chủ thể hợp đồng'
        "end_date": 26,        # 'Ngày kết thúc HĐ'
        "payment_cycle": 70,   # 'Chu kỳ thanh toán'
        "account_owner": 87,   # 'Chủ tài khoản'
        "account_no": 88,      # 'Số tài khoản'
        "bank_name": 89,       # 'Ngân hàng'
        "bank_branch": 90,     # 'Chi nhánh'
        "to_vt": 91,           # 'Tổ'
        "dat_muc_tieu_1245": 11, # 'Đạt mục tiêu 1245 (trước đàm phán)'
        "duoc_thanh_toan_1245": 12, # 'Được thanh toán theo 1245'
        "site_type": 8         # 'HTCS/ MBF/ VNPT'
    }
    
    # Try to scan and update mapping dynamically
    for idx, h in enumerate(headers):
        if ("mã trạm" in h or h == "id trạm") and "erp" not in h:
            mapping["site_id"] = idx
        elif "chủ thể hợp đồng" in h or "bên cho thuê" in h or h == "chủ nhà":
            mapping["owner"] = idx
        elif "ngày kết thúc hđ" in h or h == "hạn hợp đồng":
            mapping["end_date"] = idx
        elif "chu kỳ thanh toán" in h or h == "chu kỳ":
            mapping["payment_cycle"] = idx
        elif "đã thanh toán đến ngày" in h:
            mapping["paid_until_date"] = idx
        elif "đạt mục tiêu 1245" in h:
            mapping["dat_muc_tieu_1245"] = idx
        elif "được thanh toán theo 1245" in h:
            mapping["duoc_thanh_toan_1245"] = idx
        elif "chủ tài khoản" in h:
            mapping["account_owner"] = idx
            # Bank details are strictly sequential following account_owner
            mapping["account_no"] = idx + 1
            mapping["bank_name"] = idx + 2
            mapping["bank_branch"] = idx + 3
            mapping["to_vt"] = idx + 4
        elif "htcs" in h:
            mapping["site_type"] = idx
        elif "địa chỉ liên hệ" in h:
            mapping["contact_addr"] = idx
        elif "số hđ" in h and "cũ" not in h:
            mapping["contract_no"] = idx
        elif "ngày ký" in h or h == "ngày hợp đồng":
            mapping["contract_date"] = idx
        elif "điện thoại" in h:
            mapping["phone"] = idx
            
    # Hardcode these because there are multiple columns with similar names
    if "address_old" not in mapping:
        mapping["address_old"] = 35
    if "address_new" not in mapping:
        mapping["address_new"] = 41

    return mapping
