import pandas as pd
from typing import Dict, List, Tuple
from .data_utils import parse_numeric_value

def calculate_pricing_breakdown(df: pd.DataFrame, r_idx: int, offset: int, loaded_online: bool) -> Tuple[Dict[str, float], float, List[Dict]]:
    """
    Extracts pricing components from the spreadsheet and calculates the final breakdown.
    Returns:
        prices: Dictionary with mb, pm, mfd, cot, giam_tru, cot_rounded
        new_price_val: The total calculated price
        other_items: List of other extra items
    """
    # We will ignore 'offset' and use exact column indices for the price frame:
    # 48: Mặt bằng-QĐ 02
    mb_raw = parse_numeric_value(df.iloc[r_idx, 48])
    
    # 49 to 54: phòng máy mặt đất -> Bệ Shelter (có cọc cừ)
    pm_raw = 0.0
    for col_i in range(49, 55):
        val = parse_numeric_value(df.iloc[r_idx, col_i])
        if val > 0:
            pm_raw = val
            break
            
    # 56: Phòng MFĐ
    mfd_raw = parse_numeric_value(df.iloc[r_idx, 56])
    
    # 57 to 59: cột anten mặt đất <35m -> cột anten trên mái
    cot_raw = 0.0
    for col_i in range(57, 60):
        val = parse_numeric_value(df.iloc[r_idx, col_i])
        if val > 0:
            cot_raw = val
            break
            
    # 68: Giảm trừ dùng chung
    giam_tru_raw = parse_numeric_value(df.iloc[r_idx, 68])
    
    # Google Sheets might export small numbers representing thousands
    if loaded_online:
        if 0 < abs(mb_raw) < 10000: mb_raw *= 1000
        if 0 < abs(pm_raw) < 10000: pm_raw *= 1000
        if 0 < abs(mfd_raw) < 10000: mfd_raw *= 1000
        if 0 < abs(cot_raw) < 10000: cot_raw *= 1000
        if 0 < abs(giam_tru_raw) < 10000: giam_tru_raw *= 1000
        
    # Auxiliary Extra Items scanning (Indices 60 to 67)
    # 60: Tiếp đất, 61: Điện trong nhà, 62: Điện ngoài, 63: Điều hòa, 64-66: MPĐ, 67: Bảo vệ
    other_items = []
    other_items_raw_total = 0.0
    other_items_pay_total = 0.0
    for col_i in range(60, 68):
        val = parse_numeric_value(df.iloc[r_idx, col_i])
        if val > 0:
            if loaded_online and 0 < abs(val) < 10000:
                val *= 1000
            raw_val = val
            pay_val = (int(raw_val) // 50000) * 50000
            try:
                title = str(df.iloc[6, col_i + offset]).strip()
            except Exception:
                title = ""
            if not title or title.lower() == 'nan':
                title = f"Hạng mục Index {col_i}"
            other_items.append({
                "title": title.capitalize(),
                "raw": raw_val,
                "pay": pay_val
            })
            other_items_raw_total += raw_val
            other_items_pay_total += pay_val
            
    # Khung giá gốc không làm tròn
    cot_price_pay = cot_raw + giam_tru_raw
    
    # Layer 2: Temporary sum rounded down to nearest 50,000 for standard compliance (giá thuê mới làm tròn 50k)
    temp_total = mb_raw + pm_raw + mfd_raw + cot_price_pay + other_items_raw_total
    new_price_val = (int(temp_total) // 50000) * 50000
    
    # Trả về các thành phần nguyên gốc (không làm tròn)
    prices = {
        "mb": mb_raw,
        "pm": pm_raw,
        "mfd": mfd_raw,
        "cot": cot_raw,
        "giam_tru": giam_tru_raw,
        "cot_rounded": cot_price_pay
    }
    
    return prices, new_price_val, other_items
