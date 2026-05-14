import pandas as pd
from typing import Dict, List, Tuple
from datetime import datetime, timedelta
import calendar
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
            
    # Làm tròn hạng mục Cột (giống logic cloud_document_generator.py)
    cot_price_pay = ((int(cot_raw) + int(giam_tru_raw)) // 50000) * 50000
    
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


def get_last_day_of_month(year: int, month: int) -> int:
    """Returns the last day of the given month/year."""
    return calendar.monthrange(year, month)[1]


def calculate_aligned_cycles(start_date_str: str, cycle_months: int, term_years: int, monthly_price: float) -> Dict:
    """
    Calculates aligned payment cycles and final contract end date.
    Cycle 1: From start_date to end of month after N months.
    Contract End: Last day of the final month (Start + Term).
    """
    try:
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
    except ValueError:
        # Fallback if format is different
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except:
            return {"error": "Invalid date format"}

    # 1. Calculate Contract End Date
    is_exact_month_start = start_date.day == 1
    end_year = start_date.year + term_years
    
    if is_exact_month_start:
        # 01/06/2026 -> 31/05/2031
        end_month = start_date.month - 1
        if end_month == 0:
            end_month = 12
            end_year -= 1
    else:
        # 09/04/2026 -> 30/04/2031
        end_month = start_date.month
        
    last_day = get_last_day_of_month(end_year, end_month)
    final_contract_end = datetime(end_year, end_month, last_day)

    cycles = []
    current_start = start_date
    
    # Cycle 1: Align to end of month after cycle_months
    # Logic: 
    # - Nếu bắt đầu ngày 1: Kỳ 1 tròn cycle_months (VD: 01/05 -> 31/10)
    # - Nếu bắt đầu ngày lẻ: Kỳ 1 = ngày lẻ + cycle_months (VD: 09/04 -> 31/10)
    is_exact_month_start = start_date.day == 1
    
    if is_exact_month_start:
        c1_end_month_index = (start_date.month + cycle_months - 1)
    else:
        c1_end_month_index = (start_date.month + cycle_months)
        
    c1_end_year = start_date.year + (c1_end_month_index // 12)
    c1_end_month = (c1_end_month_index % 12)
    if c1_end_month == 0:
        c1_end_month = 12
        c1_end_year -= 1
    
    c1_end_day = get_last_day_of_month(c1_end_year, c1_end_month)
    c1_end_date = datetime(c1_end_year, c1_end_month, c1_end_day)
    
    # Calculate Cycle 1 Price
    if is_exact_month_start:
        c1_total = round(monthly_price * cycle_months)
    else:
        days_in_start_month = get_last_day_of_month(start_date.year, start_date.month)
        days_worked_in_start_month = days_in_start_month - start_date.day + 1
        c1_price_partial = (monthly_price / 30) * days_worked_in_start_month
        c1_price_full = monthly_price * cycle_months
        c1_total = round(c1_price_partial + c1_price_full)
    
    cycles.append({
        "index": 1,
        "start": current_start.strftime("%d/%m/%Y"),
        "end": c1_end_date.strftime("%d/%m/%Y"),
        "amount": c1_total,
        "is_partial": True
    })
    
    # Subsequent Cycles
    current_start = c1_end_date + timedelta(days=1)
    idx = 2
    
    while current_start < final_contract_end:
        # Each subsequent cycle starts at 01 of month and ends at end of month after cycle_months
        # But wait, the user said Kỳ 2 bắt đầu mùng 01 tháng sau.
        # If C1 ends 31/10, C2 starts 01/11.
        
        # Calculate C(idx) end
        target_end_month_index = (current_start.month + cycle_months - 2) # 0-indexed month
        c_end_year = current_start.year + (target_end_month_index // 12)
        c_end_month = (target_end_month_index % 12) + 1
        
        c_end_day = get_last_day_of_month(c_end_year, c_end_month)
        c_end_date = datetime(c_end_year, c_end_month, c_end_day)
        
        # Check if we exceeded contract end
        if c_end_date > final_contract_end:
            c_end_date = final_contract_end
            # Recalculate partial price if it's the last cycle and it's shorter
            # For simplicity, assume user wants it aligned.
            # But let's check if it's exactly cycle_months
            months_diff = (c_end_date.year - current_start.year) * 12 + (c_end_date.month - current_start.month) + 1
            c_total = monthly_price * months_diff
        else:
            c_total = monthly_price * cycle_months
            
        cycles.append({
            "index": idx,
            "start": current_start.strftime("%d/%m/%Y"),
            "end": c_end_date.strftime("%d/%m/%Y"),
            "amount": round(c_total),
            "is_partial": False
        })
        
        current_start = c_end_date + timedelta(days=1)
        idx += 1
        
    return {
        "start_date": start_date.strftime("%d/%m/%Y"),
        "end_date": final_contract_end.strftime("%d/%m/%Y"),
        "cycles": cycles
    }
