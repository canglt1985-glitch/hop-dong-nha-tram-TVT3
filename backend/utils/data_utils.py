import pandas as pd
from typing import Dict
from datetime import datetime, date

def format_date_vn(val) -> str:
    """
    Standardizes any date input (datetime, date, Timestamp, ISO string 'YYYY-MM-DD',
    'YYYY-MM-DD HH:MM:SS', 'DD/MM/YYYY', Excel serial float, etc.) to 'DD/MM/YYYY' format.
    Returns empty string if val is empty/NaN, or original string if parsing fails.
    """
    if pd.isna(val) or val is None:
        return ""
    if isinstance(val, (datetime, date, pd.Timestamp)):
        return val.strftime("%d/%m/%Y")
    
    val_str = str(val).strip()
    if not val_str or val_str.lower() in ["nan", "none", "-", "null"]:
        return ""

    # Truncate time part if present (e.g. '2026-03-31 00:00:00' -> '2026-03-31')
    date_part = val_str.split(" ")[0].split("T")[0].strip()

    # Try common strptime formats
    formats = [
        "%d/%m/%Y",
        "%Y-%m-%d",
        "%d-%m-%Y",
        "%d.%m.%Y",
        "%Y/%m/%d"
    ]
    for fmt in formats:
        try:
            dt = datetime.strptime(date_part, fmt)
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            pass

    # Try full timestamp formats
    full_formats = [
        "%Y-%m-%d %H:%M:%S",
        "%d/%m/%Y %H:%M:%S",
        "%Y-%m-%dT%H:%M:%S"
    ]
    for fmt in full_formats:
        try:
            dt = datetime.strptime(val_str, fmt)
            return dt.strftime("%d/%m/%Y")
        except ValueError:
            pass

    # Try Excel serial date number
    try:
        num = float(val_str)
        if 10000 < num < 100000:
            dt = datetime(1899, 12, 30) + pd.Timedelta(days=num)
            return dt.strftime("%d/%m/%Y")
    except Exception:
        pass

    return val_str


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
        "site_type": 8,         # 'HTCS/ MBF/ VNPT'
        "hs_phap_ly": 42        # 'Hồ sơ pháp lý'
    }
    
    # Try to scan and update mapping dynamically
    found_keys = set()
    for idx, h in enumerate(headers):
        if ("mã trạm" in h or h == "id trạm") and "erp" not in h:
            if "site_id" not in found_keys: mapping["site_id"] = idx; found_keys.add("site_id")
        elif "chủ thể hợp đồng" in h or "bên cho thuê" in h or h == "chủ nhà":
            if "owner" not in found_keys: mapping["owner"] = idx; found_keys.add("owner")
            elif "new_owner" not in found_keys: mapping["new_owner"] = idx; found_keys.add("new_owner")
        elif "ngày kết thúc hđ" in h or h == "hạn hợp đồng":
            if "end_date" not in found_keys: mapping["end_date"] = idx; found_keys.add("end_date")
        elif "đã thanh toán đến ngày" in h:
            if "paid_until_date" not in found_keys: mapping["paid_until_date"] = idx; found_keys.add("paid_until_date")
        elif "chu kỳ thanh toán" in h or h == "chu kỳ thanh toán":
            if "payment_cycle" not in found_keys: mapping["payment_cycle"] = idx; found_keys.add("payment_cycle")
        elif "hồ sơ pháp lý" in h or "pháp lý" in h:
            if "hs_phap_ly" not in found_keys: mapping["hs_phap_ly"] = idx; found_keys.add("hs_phap_ly")
        elif "đạt mục tiêu 1245" in h:
            if "dat_muc_tieu_1245" not in found_keys: mapping["dat_muc_tieu_1245"] = idx; found_keys.add("dat_muc_tieu_1245")
        elif "được thanh toán theo 1245" in h:
            if "duoc_thanh_toan_1245" not in found_keys: mapping["duoc_thanh_toan_1245"] = idx; found_keys.add("duoc_thanh_toan_1245")
        elif "chủ tài khoản" in h:
            if "account_owner" not in found_keys:
                mapping["account_owner"] = idx
                mapping["account_no"] = idx + 1
                mapping["bank_name"] = idx + 2
                mapping["bank_branch"] = idx + 3
                mapping["to_vt"] = idx + 4
                found_keys.add("account_owner")
            elif "new_bank_owner" not in found_keys:
                mapping["new_bank_owner"] = idx
                mapping["new_bank_no"] = idx + 1
                mapping["new_bank_name"] = idx + 2
                mapping["new_bank_branch"] = idx + 3
                found_keys.add("new_bank_owner")
        elif "htcs" in h:
            if "site_type" not in found_keys: mapping["site_type"] = idx; found_keys.add("site_type")
        elif "địa chỉ liên hệ" in h:
            if "contact_addr" not in found_keys: mapping["contact_addr"] = idx; found_keys.add("contact_addr")
            elif "new_owner_address" not in found_keys: mapping["new_owner_address"] = idx; found_keys.add("new_owner_address")
        elif "số hđ" in h and "cũ" not in h:
            if "contract_no" not in found_keys: mapping["contract_no"] = idx; found_keys.add("contract_no")
        elif "ngày ký" in h or h == "ngày hợp đồng":
            if "contract_date" not in found_keys: mapping["contract_date"] = idx; found_keys.add("contract_date")
        elif "điện thoại" in h:
            if "phone" not in found_keys: mapping["phone"] = idx; found_keys.add("phone")
            elif "new_owner_phone" not in found_keys: mapping["new_owner_phone"] = idx; found_keys.add("new_owner_phone")
        elif "kinh độ" in h or "longitude" in h:
            if "longitude" not in found_keys: mapping["longitude"] = idx; found_keys.add("longitude")
        elif "vĩ độ" in h or "latitude" in h:
            if "latitude" not in found_keys: mapping["latitude"] = idx; found_keys.add("latitude")
            
    # Hardcode these because there are multiple columns with similar names
    if "address_old" not in mapping:
        mapping["address_old"] = 35
    if "address_new" not in mapping:
        mapping["address_new"] = 41
    if "longitude" not in mapping:
        mapping["longitude"] = 97
    if "latitude" not in mapping:
        mapping["latitude"] = 98

    return mapping
