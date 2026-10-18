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
            
    # Layer 2: Temporary sum rounded down to nearest 50,000 for standard compliance (giá thuê mới làm tròn 50k)
    temp_total = mb_raw + pm_raw + mfd_raw + cot_raw + giam_tru_raw + other_items_raw_total
    new_price_val = (int(temp_total) // 50000) * 50000
    
    # Hạng mục Cột:
    # 1. Nếu Vượt/Bằng khung (new_price_val >= temp_total): Giữ 100% giá trị quy định thực tế.
    # 2. Nếu Dưới khung (new_price_val < temp_total): Giới hạn Mặt bằng <= mb_raw, phần chênh dồn vào Cột anten để Mặt bằng không vượt khung.
    cot_raw_net = cot_raw + giam_tru_raw
    if new_price_val >= temp_total:
        cot_price_pay = cot_raw_net if cot_raw_net > 0 else 0
    else:
        desired_mb = mb_raw if mb_raw > 0 else 0
        if desired_mb + pm_raw + mfd_raw + other_items_pay_total <= new_price_val:
            cot_price_pay = max(0.0, new_price_val - desired_mb - pm_raw - mfd_raw - other_items_pay_total)
        else:
            cot_price_pay = 0.0
    
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


def calculate_aligned_cycles(
    start_date_str: str, 
    cycle_months: int, 
    term_years: int, 
    monthly_price: float, 
    forced_end_date_str: str = None,
    old_price: float = None,
    split_date_str: str = "01/10/2025"
) -> Dict:
    """
    Calculates aligned payment cycles and final contract end date.
    Cycle 1: From start_date to end of month after N months.
    Contract End: Last day of the final month (Start + Term), or forced_end_date if provided.
    Supports split pricing transition from old_price (before split_date) to monthly_price (from split_date onwards).
    """
    try:
        start_date = datetime.strptime(start_date_str, "%d/%m/%Y")
    except ValueError:
        try:
            start_date = datetime.strptime(start_date_str, "%Y-%m-%d")
        except:
            return {"error": "Invalid date format"}

    if forced_end_date_str:
        try:
            final_contract_end = datetime.strptime(forced_end_date_str, "%d/%m/%Y")
        except:
            try:
                final_contract_end = datetime.strptime(forced_end_date_str, "%Y-%m-%d")
            except:
                final_contract_end = start_date
    else:
        # Calculate Contract End Date if not forced
        is_exact_month_start = start_date.day == 1
        end_year = start_date.year + term_years
        
        if is_exact_month_start:
            end_month = start_date.month - 1
            if end_month == 0:
                end_month = 12
                end_year -= 1
        else:
            end_month = start_date.month
            
        last_day = get_last_day_of_month(end_year, end_month)
        final_contract_end = datetime(end_year, end_month, last_day)

    try:
        split_date = datetime.strptime(split_date_str, "%d/%m/%Y")
    except:
        split_date = datetime(2025, 10, 1)

    # Helper function to calculate a cycle's amount month-by-month
    def get_cycle_amount(c_start, c_end):
        if old_price is None or old_price <= 0 or old_price == monthly_price:
            # Traditional calculation (consistent and fast)
            is_exact = (c_start.day == 1) and (c_end.day == get_last_day_of_month(c_end.year, c_end.month))
            if is_exact:
                m_diff = (c_end.year - c_start.year) * 12 + (c_end.month - c_start.month) + 1
                return round(monthly_price * m_diff)
            else:
                # Month-by-month calculation for partial start/end dates
                total_cycle_amount = 0.0
                curr = datetime(c_start.year, c_start.month, 1)
                end_month_bound = datetime(c_end.year, c_end.month, 1)
                while curr <= end_month_bound:
                    m_start = max(c_start, curr)
                    m_end_day = get_last_day_of_month(curr.year, curr.month)
                    m_end = min(c_end, datetime(curr.year, curr.month, m_end_day))
                    
                    active_days = (m_end - m_start).days + 1
                    total_days_in_month = m_end_day
                    
                    if active_days == total_days_in_month:
                        total_cycle_amount += monthly_price
                    else:
                        total_cycle_amount += (monthly_price / float(total_days_in_month)) * active_days
                        
                    if curr.month == 12:
                        curr = datetime(curr.year + 1, 1, 1)
                    else:
                        curr = datetime(curr.year, curr.month + 1, 1)
                return round(total_cycle_amount)

        # Split pricing month-by-month
        total_cycle_amount = 0.0
        curr = datetime(c_start.year, c_start.month, 1)
        end_month_bound = datetime(c_end.year, c_end.month, 1)
        
        while curr <= end_month_bound:
            # Active days of this month inside [c_start, c_end]
            m_start = max(c_start, curr)
            m_end_day = get_last_day_of_month(curr.year, curr.month)
            m_end = min(c_end, datetime(curr.year, curr.month, m_end_day))
            
            active_days = (m_end - m_start).days + 1
            total_days_in_month = m_end_day
            
            # Determine price for this month: old_price before split_date, new_price from split_date
            current_month_price = old_price if m_start < split_date else monthly_price
            
            if active_days == total_days_in_month:
                total_cycle_amount += current_month_price
            else:
                total_cycle_amount += (current_month_price / float(total_days_in_month)) * active_days
                
            # Move to next month
            if curr.month == 12:
                curr = datetime(curr.year + 1, 1, 1)
            else:
                curr = datetime(curr.year, curr.month + 1, 1)
                
        return round(total_cycle_amount)

    cycles = []
    current_start = start_date
    
    # Cycle 1: Align to end of month after cycle_months
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
    if c1_end_date > final_contract_end:
        c1_end_date = final_contract_end
    
    c1_amt = get_cycle_amount(current_start, c1_end_date)
    cycles.append({
        "index": 1,
        "start": current_start.strftime("%d/%m/%Y"),
        "end": c1_end_date.strftime("%d/%m/%Y"),
        "amount": c1_amt,
        "is_partial": not is_exact_month_start
    })
    
    # Subsequent Cycles
    current_start = c1_end_date + timedelta(days=1)
    idx = 2
    
    while current_start < final_contract_end:
        target_end_month_index = (current_start.month + cycle_months - 2) # 0-indexed month
        c_end_year = current_start.year + (target_end_month_index // 12)
        c_end_month = (target_end_month_index % 12) + 1
        
        c_end_day = get_last_day_of_month(c_end_year, c_end_month)
        c_end_date = datetime(c_end_year, c_end_month, c_end_day)
        
        # Check if we exceeded contract end
        if c_end_date > final_contract_end:
            c_end_date = final_contract_end
            
        c_amt = get_cycle_amount(current_start, c_end_date)
        cycles.append({
            "index": idx,
            "start": current_start.strftime("%d/%m/%Y"),
            "end": c_end_date.strftime("%d/%m/%Y"),
            "amount": c_amt,
            "is_partial": False
        })
        
        current_start = c_end_date + timedelta(days=1)
        idx += 1
        
    return {
        "start_date": start_date.strftime("%d/%m/%Y"),
        "end_date": final_contract_end.strftime("%d/%m/%Y"),
        "cycles": cycles
    }
