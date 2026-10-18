import os
import docx
from datetime import datetime
from dateutil.relativedelta import relativedelta
from docx.oxml.ns import qn
import copy
import calendar
from utils.pricing_utils import calculate_aligned_cycles
from utils.data_utils import format_date_vn

def format_vn_currency(amount):
    try:
        if amount is None or amount == "": return "0"
        return "{:,.0f}".format(float(amount)).replace(",", ".")
    except Exception:
        return "0"

def number_to_vietnamese_words(number):
    try: number = int(number)
    except: return ""
    if number == 0: return "Không"
    units = ["", "một", "hai", "ba", "bốn", "năm", "sáu", "bảy", "tám", "chín"]
    def read_three_digits(n, is_first=False):
        hundreds = n // 100
        tens = (n % 100) // 10
        ones = n % 10
        res = []
        if hundreds > 0: res.append(units[hundreds] + " trăm")
        elif not is_first: res.append("không trăm")
        if tens > 0:
            if tens == 1: res.append("mười")
            else: res.append(units[tens] + " mươi")
        elif (hundreds > 0 or not is_first) and ones > 0:
            res.append("lẻ")
        if ones > 0:
            if ones == 1 and tens > 1: res.append("mốt")
            elif ones == 5 and tens > 0: res.append("lăm")
            else: res.append(units[ones])
        return " ".join(res)
    groups = []
    temp = number
    while temp > 0:
        groups.append(temp % 1000)
        temp //= 1000
    group_units = ["", "nghìn", "triệu", "tỷ", "nghìn tỷ", "triệu tỷ"]
    words = []
    for idx, val in enumerate(groups):
        if val > 0:
            part = read_three_digits(val, idx == len(groups) - 1)
            unit = group_units[idx]
            if unit: words.append(part + " " + unit)
            else: words.append(part)
    words.reverse()
    text = " ".join(words)
    text = " ".join(text.split()).strip()
    return text[0].upper() + text[1:]

def replace_tag_in_runs(p, tag, replacement):
    if tag not in p.text: return False
    replaced = False
    for run in p.runs:
        if tag in run.text:
            run.text = run.text.replace(tag, str(replacement))
            run.font.name = "Times New Roman"
            run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
            replaced = True
    if not replaced:
        p.text = p.text.replace(tag, str(replacement))
        for run in p.runs:
            run.font.name = "Times New Roman"
            run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
        replaced = True
    return replaced

def calculate_contract_dates(expiry_date_val, extension_years=5):
    try:
        formatted_exp = format_date_vn(expiry_date_val)
        if formatted_exp:
            exp_date = datetime.strptime(formatted_exp, "%d/%m/%Y")
        elif isinstance(expiry_date_val, datetime): 
            exp_date = expiry_date_val
        else:
            exp_date = datetime(2026, 4, 9)
                
        # Ngày bắt đầu HĐ mới = Ngày sau ngày hết hạn cũ
        start_date = exp_date + relativedelta(days=1)
        
        # Ngày kết thúc chuẩn hóa:
        is_exact_month_start = start_date.day == 1
        target_end_year = start_date.year + extension_years
        
        if is_exact_month_start:
            # 01/06/2026 -> 31/05/2031 (nếu 5 năm)
            target_end_month = start_date.month - 1
            if target_end_month == 0:
                target_end_month = 12
                target_end_year -= 1
        else:
            # 09/04/2026 -> 30/04/2031 (nếu 5 năm)
            target_end_month = start_date.month
            
        last_day = calendar.monthrange(target_end_year, target_end_month)[1]
        end_date = datetime(target_end_year, target_end_month, last_day)
        
        return start_date, end_date
    except Exception:
        return datetime(2026, 4, 9), datetime(2026 + extension_years, 4, 30)


def generate_document_from_cloud(site_data, template_path, output_dir, prefix, template_type=None, apply_vb1245=True, apply_extension=False, extension_years=5, custom_start_date=None):
    site_id = site_data.get("site_id", "")
    owner_name = site_data.get("owner", "")
    
    # Coordinates & Address
    latitude = str(site_data.get("latitude", ""))
    longitude = str(site_data.get("longitude", ""))
    address_old = site_data.get("address_old", "")
    
    banking = site_data.get("banking_info", {})
    account_owner = banking.get("account_owner", "") or owner_name
    account_no = banking.get("account_no", "")
    bank_name = banking.get("bank_name", "")
    bank_branch = banking.get("bank_branch", "")
    full_bank_name = f"{bank_name} - {bank_branch}" if bank_branch else bank_name

    # Extract exact original end_date
    raw_expiry = site_data.get("end_date", "")
    original_end_date_dt = None
    if raw_expiry:
        try:
            if isinstance(raw_expiry, datetime): original_end_date_dt = raw_expiry
            else: original_end_date_dt = datetime.strptime(str(raw_expiry)[:10], "%d/%m/%Y")
        except Exception:
            try:
                original_end_date_dt = datetime.strptime(str(raw_expiry)[:10], "%Y-%m-%d")
            except Exception:
                pass

    # Parse effective date
    effective_str = site_data.get("effective_date", "")
    eff_dt = None
    if effective_str and str(effective_str).strip() not in ["nan", "None", "", "-"]:
        try:
            eff_dt = datetime.strptime(str(effective_str)[:10], "%d/%m/%Y")
        except:
            pass

    # Prices calculation to determine price reduction
    old_price_val = float(site_data.get("old_price") or 0)
    provided_new_price = int(site_data.get("new_price", 0))
    new_price_approx = provided_new_price if provided_new_price > 0 else old_price_val
    has_reduction = (old_price_val > new_price_approx) and (new_price_approx > 0)

    # Calculate default contract dates
    start_date_dt, extended_end_date_dt = calculate_contract_dates(raw_expiry, extension_years)

    # Check custom_start_date
    if custom_start_date and str(custom_start_date).strip() not in ["", "nan", "None"]:
        try:
            formatted_c = format_date_vn(str(custom_start_date).strip())
            if formatted_c:
                start_date_dt = datetime.strptime(formatted_c, "%d/%m/%Y")
                target_end_year = start_date_dt.year + extension_years
                target_end_month = start_date_dt.month - 1 if start_date_dt.day == 1 else start_date_dt.month
                if target_end_month == 0:
                    target_end_month = 12
                    target_end_year -= 1
                last_day = calendar.monthrange(target_end_year, target_end_month)[1]
                extended_end_date_dt = datetime(target_end_year, target_end_month, last_day)
        except Exception as custom_err:
            print(f"Warning: Failed to parse custom_start_date '{custom_start_date}': {custom_err}")
    elif apply_vb1245 and has_reduction:
        # Override start billing date for price reductions under VB1245
        if eff_dt:
            start_date_dt = eff_dt
        else:
            start_date_dt = datetime(2025, 10, 1)

    # For pure reduction templates without extension, keep original contract expiry
    if template_type == "phu_luc_giam_gia":
        if original_end_date_dt:
            extended_end_date_dt = original_end_date_dt
                
    start_date_str = start_date_dt.strftime("%d/%m/%Y")
    end_date_str = extended_end_date_dt.strftime("%d/%m/%Y")
    
    # Always use the extended 5-year date for the contract term in these templates unless overridden above
    end_contract_dt = extended_end_date_dt
    end_contract = end_contract_dt
    
    # OLD_END_DATE calculation
    if original_end_date_dt:
        old_end_date_str = original_end_date_dt.strftime("%d/%m/%Y")
    else:
        old_end_date_str = str(raw_expiry) if raw_expiry else ""
    
    # Prices
    prices = site_data.get("prices_breakdown", {})
    mb_raw = float(prices.get("mb", 0))
    pm_raw = float(prices.get("pm", 0))
    mfd_raw = float(prices.get("mfd", 0))
    cot_raw = float(prices.get("cot", 0))
    giam_tru_raw = float(prices.get("giam_tru", 0))
    vhkt_raw = float(prices.get("vhkt", 0))
    
    # Lớp 2: Tính tổng quy định khung ban đầu
    temp_total = mb_raw + pm_raw + mfd_raw + cot_raw + giam_tru_raw + vhkt_raw
    
    provided_new_price = int(site_data.get("new_price", 0))
    if provided_new_price > 0:
        new_price_val = provided_new_price
    else:
        # If pure extension, keep old price
        if template_type in ["phu_luc_gia_han", "phu_luc_gia_han_ngan_han"]:
            new_price_val = (int(site_data.get("old_price", 0) or 0) // 50000) * 50000
        else:
            new_price_val = (int(temp_total) // 50000) * 50000
            
    # LOGIC CHIA PHÂN BỔ HẠNG MỤC:
    # 1. Nếu Vượt/Bằng khung quy định (new_price_val >= temp_total):
    #    Các hạng mục phụ (Cột, PM, MFĐ, VHKT) giữ 100% giá trị quy định thực tế.
    #    Mặt bằng nhận phần còn lại (vượt khung dồn vào mặt bằng).
    # 2. Nếu Dưới khung quy định (new_price_val < temp_total):
    #    Các hạng mục phụ (PM, MFĐ, VHKT) giữ nguyên giá quy định.
    #    Mặt bằng được giới hạn tối đa là mb_raw (không được vượt khung QĐ02).
    #    Phần chênh lệch dưới khung được dồn sang Cột anten để không hạng mục nào bị vượt khung.
    cot_raw_net = cot_raw + giam_tru_raw
    if new_price_val >= temp_total:
        cot_price_pay = cot_raw_net if cot_raw_net > 0 else 0
        vhkt_price_pay = vhkt_raw if vhkt_raw > 0 else 0
        pm_price_pay = pm_raw if pm_raw > 0 else 0
        mfd_price_pay = mfd_raw if mfd_raw > 0 else 0
        mb_price_pay = new_price_val - pm_price_pay - mfd_price_pay - cot_price_pay - vhkt_price_pay
    else:
        vhkt_price_pay = vhkt_raw if vhkt_raw > 0 else 0
        pm_price_pay = pm_raw if pm_raw > 0 else 0
        mfd_price_pay = mfd_raw if mfd_raw > 0 else 0
        
        # Mặt bằng lấy tối đa bằng mb_raw (không được vượt khung mb_raw khi tổng không vượt)
        desired_mb = mb_raw if mb_raw > 0 else 0
        if desired_mb + pm_price_pay + mfd_price_pay + vhkt_price_pay <= new_price_val:
            mb_price_pay = desired_mb
            cot_price_pay = max(0.0, new_price_val - mb_price_pay - pm_price_pay - mfd_price_pay - vhkt_price_pay)
        else:
            mb_price_pay = max(0.0, new_price_val - pm_price_pay - mfd_price_pay - vhkt_price_pay)
            cot_price_pay = 0.0

    
    new_price_str = format_vn_currency(new_price_val)
    new_price_text = number_to_vietnamese_words(new_price_val) + " đồng"
    
    # PRICE_PHRASING calculation based on difference between old_price and new_price
    old_price_val = float(site_data.get("old_price") or 0)
    if not apply_vb1245 or template_type in ["phu_luc_gia_han", "phu_luc_gia_han_ngan_han"]:
        price_phrasing = f"{new_price_str} đồng/tháng (bằng chữ: {new_price_text})"
    elif old_price_val > new_price_val:
        old_price_str = format_vn_currency(old_price_val)
        price_phrasing = f"giảm từ {old_price_str} đồng/tháng xuống còn {new_price_str} đồng/tháng (bằng chữ: {new_price_text})"
    elif old_price_val < new_price_val and old_price_val > 0:
        old_price_str = format_vn_currency(old_price_val)
        price_phrasing = f"tăng từ {old_price_str} đồng/tháng lên {new_price_str} đồng/tháng (bằng chữ: {new_price_text})"
    else:
        price_phrasing = f"{new_price_str} đồng/tháng (bằng chữ: {new_price_text})"

    
    # Calculate Deduction Text & Paid Info
    deduction_text = ""
    total_deduction = 0
    paid_until_raw = site_data.get("paid_until_date", "")
    paid_until = format_date_vn(paid_until_raw)
    paid_dt = None
    if paid_until:
        try:
            paid_dt = datetime.strptime(paid_until, "%d/%m/%Y")
        except Exception:
            pass

    if paid_dt and apply_vb1245:
        start_dt = datetime(2025, 10, 1)
        if paid_dt >= start_dt:
            # ONLY compute retroactive deduction for CSHT
            site_type_val = str(site_data.get("site_type", "")).strip().upper()
            is_mbf = "MBF" in site_type_val or "MOBIFONE" in site_type_val or "MAT" in site_type_val or "MẶT" in site_type_val
            
            if not is_mbf:
                try:
                    paid_dt_adjusted = paid_dt + relativedelta(days=1)
                    diff = relativedelta(paid_dt_adjusted, start_dt)
                    months_overpaid = diff.years * 12 + diff.months + (diff.days / 30.0)
                    
                    old_p = float(site_data.get("old_price", 0) or 0)
                    new_p = float(new_price_val)
                    diff_per_month = old_p - new_p
                    
                    if diff_per_month > 0 and months_overpaid > 0:
                        total_deduction = diff_per_month * months_overpaid
                        deduction_text = f"Giảm trừ số tiền {format_vn_currency(total_deduction)} đồng đã thanh toán từ 01/10/2025 đến {paid_until} vào kỳ thanh toán tiếp theo."
                    else:
                        deduction_text = f"Giảm trừ số tiền đã thanh toán từ 01/10/2025 đến {paid_until} vào kỳ thanh toán tiếp theo."
                except Exception:
                    deduction_text = f"Giảm trừ số tiền đã thanh toán từ 01/10/2025 đến {paid_until} vào kỳ thanh toán tiếp theo."
    
    # Generate CSHT List dynamically
    csht_list = (
        "Vị trí đặt thiết bị: phòng có sẵn của chủ trạm, diện tích 3x3m, theo tiêu chuẩn của MobiFone.\n"
        "- Vị trí đặt máy nổ: phòng có sẵn của chủ trạm, diện tích 3mx2m, theo tiêu chuẩn của MobiFone.\n"
        "- Cột anten: cột dây co dưới mặt đất cao 36m có sẵn của chủ trạm.\n"
        "- Hệ thống tiếp đất và hệ thống lạnh: MobiFone tự trang bị."
    )

    # For pure extension, remove certificate basis
    hs_phap_ly = site_data.get("hs_phap_ly", "")
    if template_type in ["phu_luc_gia_han", "phu_luc_gia_han_ngan_han"]:
        certificate_text = ""
    else:
        certificate_text = hs_phap_ly if hs_phap_ly and hs_phap_ly != "nan" else "................................................................................................................................"

    # Compute dynamic subject reason
    site_type_val = str(site_data.get("site_type", "")).strip().upper()
    is_mbf = "MBF" in site_type_val or "MOBIFONE" in site_type_val
    subject_target = "mặt bằng" if is_mbf else "cơ sở hạ tầng"

    if template_type == "phu_luc_giam_gia":
        ly_do = f"điều chỉnh giá thuê {subject_target}"
    elif template_type in ["phu_luc_gia_han", "phu_luc_gia_han_ngan_han"]:
        ly_do = f"gia hạn thời gian thuê {subject_target}"
    elif template_type in ["phu_luc_giam_gia_gia_han", "phu_luc_giam_gia_gia_han_ngan_han"]:
        ly_do = "gia hạn thời gian và điều chỉnh điều khoản"
    else:
        ly_do = ""

    replacements = {
        "{{LY_DO}}": ly_do,
        "{{ LY_DO }}": ly_do,
        "{{CERTIFICATE}}": certificate_text,
        "{{ CERTIFICATE }}": certificate_text,
        "{{SITE_ID}}": site_id,
        "{{ SITE_ID }}": site_id,
        "{{OWNER_NAME}}": owner_name,
        "{{ OWNER_NAME }}": owner_name,
        "{{ CONTRACT_NO }}": "",
        "{{CONTRACT_DATE}}": "",
        "{{ CONTRACT_DATE }}": "",
        "{{ADDRESS_OLD}}": address_old,
        "{{ ADDRESS_OLD }}": address_old,
        "{{ADDRESS_OLD{{ADDRESS_NEW}}": f"{address_old} ({site_data.get('address_new', '')})",
        "{{ADDRESS_OLD{{ADDRESS_NEW}} }": f"{address_old} ({site_data.get('address_new', '')})",
        "{{ADDRESS_NEW}}": site_data.get("address_new", ""),
        "{{ ADDRESS_NEW }}": site_data.get("address_new", ""),
        " ({{ADDRESS_NEW}})": f" ({site_data.get('address_new')})" if site_data.get("address_new") and site_data.get("address_new") != "nan" else "",
        " ({{ ADDRESS_NEW }})": f" ({site_data.get('address_new')})" if site_data.get("address_new") and site_data.get("address_new") != "nan" else "",
        "{{LONGITUDE}}": longitude,
        "{{LONGITUDE }}": longitude,
        "{{LATITUDE}}": latitude,
        "{{LATITUDE }}": latitude,
        "{{CERTIFICATE}}": certificate_text,
        "{{ CERTIFICATE }}": certificate_text,
        "{{LEGAL_DOCS}}": certificate_text,
        "{{ LEGAL_DOCS }}": certificate_text,
        "{{START_DATE}}": start_date_str,
        "{{END_DATE}}": end_date_str,
        "{{NEW_PRICE}}": new_price_str,
        "{{ NEW_PRICE }}": new_price_str,
        "{{NEW_PRICE_TEXT}}": new_price_text,
        "{{ NEW_PRICE_TEXT }}": new_price_text,
        "{{PRICE_PHRASING}}": price_phrasing,
        "{{ PRICE_PHRASING }}": price_phrasing,

        "{{ACCOUNT_OWNER}}": account_owner,
        "{{ ACCOUNT_OWNER }}": account_owner,
        "{{ACCOUNT_NO}}": account_no,
        "{{ ACCOUNT_NO }}": account_no,
        "{{BANK_NAME}}": full_bank_name,
        "{{ BANK_NAME }}": full_bank_name,
        
        "{{MB_QĐ02}}": format_vn_currency(mb_raw),
        "{{ MB_QĐ02 }}": format_vn_currency(mb_raw),
        "{{P_MB}}": format_vn_currency(mb_price_pay),
        "{{ P_MB }}": format_vn_currency(mb_price_pay),
        "{{TL_MB}}": f"{((mb_price_pay / mb_raw) - 1) * 100:.2f}%" if mb_raw != 0 else "0%",
        "{{ TL_MB }}": f"{((mb_price_pay / mb_raw) - 1) * 100:.2f}%" if mb_raw != 0 else "0%",
        
        "{{PM_1245}}": format_vn_currency(pm_raw),
        "{{ PM_1245 }}": format_vn_currency(pm_raw),
        "{{P_PM}}": format_vn_currency(pm_price_pay),
        "{{ P_PM }}": format_vn_currency(pm_price_pay),
        "{{TL_PM}}": f"{((pm_price_pay / pm_raw) - 1) * 100:.2f}%" if pm_raw != 0 else "0%",
        "{{ TL_PM }}": f"{((pm_price_pay / pm_raw) - 1) * 100:.2f}%" if pm_raw != 0 else "0%",
        
        "{{MFĐ_1245}}": format_vn_currency(mfd_raw),
        "{{ MFĐ_1245 }}": format_vn_currency(mfd_raw),
        "{{P_MFD}}": format_vn_currency(mfd_price_pay),
        "{{ P_MFD }}": format_vn_currency(mfd_price_pay),
        "{{TL_MFD}}": f"{((mfd_price_pay / mfd_raw) - 1) * 100:.2f}%" if mfd_raw != 0 else "0%",
        "{{ TL_MFD }}": f"{((mfd_price_pay / mfd_raw) - 1) * 100:.2f}%" if mfd_raw != 0 else "0%",
        
        "{{COT_1245}}": format_vn_currency(cot_raw),
        "{{ COT_1245 }}": format_vn_currency(cot_raw),
        "{{GIAM_TRU}}": format_vn_currency(giam_tru_raw),
        "{{ GIAM_TRU }}": format_vn_currency(giam_tru_raw),
        "{{COT_CHOT}}": format_vn_currency(cot_price_pay),
        "{{ COT_CHOT }}": format_vn_currency(cot_price_pay),
        "{{TL_COT}}": f"{((cot_price_pay / cot_raw_net) - 1) * 100:.2f}%" if cot_raw_net != 0 else "0%",
        "{{ TL_COT }}": f"{((cot_price_pay / cot_raw_net) - 1) * 100:.2f}%" if cot_raw_net != 0 else "0%",
        
        "{{VHKT_1245}}": format_vn_currency(vhkt_raw),
        "{{ VHKT_1245 }}": format_vn_currency(vhkt_raw),
        "{{P_VHKT}}": format_vn_currency(vhkt_price_pay),
        "{{ P_VHKT }}": format_vn_currency(vhkt_price_pay),
        "{{TL_VHKT}}": f"{((vhkt_price_pay / vhkt_raw) - 1) * 100:.2f}%" if vhkt_raw != 0 else "0%",
        "{{ TL_VHKT }}": f"{((vhkt_price_pay / vhkt_raw) - 1) * 100:.2f}%" if vhkt_raw != 0 else "0%",
        
        "{{TONG_QD}}": format_vn_currency(mb_raw + pm_raw + mfd_raw + cot_raw + giam_tru_raw + vhkt_raw),
        "{{ TONG_QD }}": format_vn_currency(mb_raw + pm_raw + mfd_raw + cot_raw + giam_tru_raw + vhkt_raw),
        "{{TONG_CHOT}}": format_vn_currency(new_price_val),
        "{{ TONG_CHOT }}": format_vn_currency(new_price_val),
        "{{TL_TONG}}": f"{((new_price_val / (mb_raw + pm_raw + mfd_raw + cot_raw + giam_tru_raw + vhkt_raw)) - 1) * 100:.2f}%" if (mb_raw + pm_raw + mfd_raw + cot_raw + giam_tru_raw + vhkt_raw) != 0 else "0%",
        
        # Additional tags for Phu Luc Giam Gia and Thanh Ly
        "{{OLD_PRICE}}": format_vn_currency(site_data.get("old_price", 0)),
        "{{ OLD_PRICE }}": format_vn_currency(site_data.get("old_price", 0)),
        "{{PHONE}}": site_data.get("phone", ""),
        "{{ PHONE }}": site_data.get("phone", ""),
        "{{CONTACT_ADDR}}": site_data.get("contact_addr", ""),
        "{{ CONTACT_ADDR }}": site_data.get("contact_addr", ""),
        "{{CONTRACT_NO}}": site_data.get("contract_no", ""),
        "{{ CONTRACT_NO }}": site_data.get("contract_no", ""),
        "{{CONTRACT_DATE}}": site_data.get("contract_date", ""),
        "{{ CONTRACT_DATE }}": site_data.get("contract_date", ""),
        "{{PAID_UNTIL_DATE}}": paid_until,
        "{{ PAID_UNTIL_DATE }}": paid_until,
        "{{OLD_END_DATE}}": old_end_date_str,
        "{{ OLD_END_DATE }}": old_end_date_str,
        "{{CSHT_LIST1}}": csht_list,
        "{{ CSHT_LIST1 }}": csht_list,
        "{{CSHT_LIST2}}": csht_list,
        "{{ CSHT_LIST2 }}": csht_list,
        "{{DEDUCTION_TEXT}}": deduction_text,
        "{{ DEDUCTION_TEXT }}": deduction_text,
        "{{REPORT_DATE}}": datetime.now().strftime('%d/%m/%Y'),
        "{{ REPORT_DATE }}": datetime.now().strftime('%d/%m/%Y'),
        "{{TOTAL_AMOUNT}}": format_vn_currency(new_price_val * 6), # Will be overridden if needed
        "{{ TOTAL_AMOUNT }}": format_vn_currency(new_price_val * 6),
        "{{CYCLES_REMAINING}}": "0",
        "{{ CYCLES_REMAINING }}": "0",
        "{{OWNER_MATCH}}": banking.get("match_status_text", ""),
        "{{ OWNER_MATCH }}": banking.get("match_status_text", ""),
        "{{EXTENSION_STATUS}}": site_data.get("ext_status", ""),
        "{{ EXTENSION_STATUS }}": site_data.get("ext_status", ""),
        
        # Party A Owner Transition specific placeholders
        "{{ OWNER_OLD_NAME }}": owner_name,
        "{{ OWNER_NEW_NAME }}": site_data.get("new_owner_info", {}).get("name") or "................................",
        "{{ OWNER_OLD_ADDRESS }}": address_old,
        "{{ OWNER_NEW_ADDRESS }}": site_data.get("new_owner_info", {}).get("address") or "................................",
        "{{ OWNER_OLD_PHONE }}": site_data.get("phone") or "................",
        "{{ OWNER_NEW_PHONE }}": site_data.get("new_owner_info", {}).get("phone") or "................",
        "{{ OWNER_OLD_CCCD }}": "................................................",
        "{{ OWNER_NEW_CCCD }}": "................................................",
        "{{ OWNER_OLD_ACCOUNT_NO }}": account_no or "................",
        "{{ OWNER_NEW_ACCOUNT_NO }}": site_data.get("new_owner_info", {}).get("bank_no") or "................",
        "{{ OWNER_OLD_BANK }}": full_bank_name or "................",
        "{{ OWNER_NEW_BANK }}": site_data.get("new_owner_info", {}).get("bank_name") or "................",
        "{{ EFFECTIVE_DATE }}": site_data.get("effective_date") or "................",
        "{{ ATTACHMENT_DEATH_CERT }}": "trích lục khai tử ................................................",
        "{{ ATTACHMENT_LAND_CERT }}": "chứng nhận quyền sử dụng đất số ................................................",
        "{{ ATTACHMENT_DESIRE_LETTER }}": "đơn đề nghị chuyển tên ngày ................................",
        "{{ LAND_ADDRESS }}": site_data.get("address_new") or address_old or "................................................",
        "{{ SITE_CODE }}": site_data.get("site_code") or site_id or "........"
    }

    doc = docx.Document(template_path)
    
    # Remove DEDUCTION_TEXT paragraph if empty to avoid floating hyphen
    if not deduction_text:
        for p in doc.paragraphs:
            if "{{DEDUCTION_TEXT}}" in p.text or "{{ DEDUCTION_TEXT }}" in p.text:
                p_element = p._element
                p_element.getparent().remove(p_element)
                p._p = p._element = None
    
    # 5. GENERATE PAYMENT TABLE (Dồn ngày lẻ vào Kỳ 1 và căn chỉnh chu kỳ 6 tháng)
    periods = []
    total_amount = 0
    cycle_months = 6
    term_years = extension_years

    # Lấy thông tin chu kỳ từ paid_dt (nếu có và áp dụng VB1245 không có custom_start_date) hoặc start_date_str
    if paid_dt and apply_vb1245 and (not custom_start_date or str(custom_start_date).strip() in ["", "nan", "None"]):
        table_start_str = (paid_dt + relativedelta(days=1)).strftime("%d/%m/%Y")
    else:
        table_start_str = start_date_str

    result = calculate_aligned_cycles(table_start_str, cycle_months, term_years, new_price_val, forced_end_date_str=end_date_str, old_price=old_price_val)
    
    if "cycles" in result:
        for c in result["cycles"]:
            amt = c["amount"]
            if c["index"] == 1 and total_deduction > 0:
                amt -= total_deduction
                
            # Chuyển đổi ngược lại format để tương thích code cũ bên dưới
            periods.append({
                "no": c["index"],
                "start": datetime.strptime(c["start"], "%d/%m/%Y"),
                "end": datetime.strptime(c["end"], "%d/%m/%Y"),
                "amount": amt
            })
            total_amount += amt
        
        end_contract = datetime.strptime(result["end_date"], "%d/%m/%Y")
        replacements["{{START_DATE}}"] = result["start_date"]
        replacements["{{ START_DATE }}"] = result["start_date"]
        replacements["{{END_DATE}}"] = result["end_date"]
        replacements["{{TOTAL_AMOUNT}}"] = format_vn_currency(total_amount)
        replacements["{{ TOTAL_AMOUNT }}"] = format_vn_currency(total_amount)

    # 6. Global Replacements
    total_replacement = f"Tổng cộng:             {format_vn_currency(total_amount)}"
    import re
    
    has_page_broken = False
    republic_count = 0
    paragraphs = list(doc.paragraphs)
    for idx, p in enumerate(paragraphs):
        if "Tổng cộng:" in p.text:
            if re.search(r'[\d\.]+', p.text):
                p.text = total_replacement
                p.paragraph_format.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.RIGHT
                for run in p.runs:
                    run.font.name = "Times New Roman"
                    run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                    run.font.size = docx.shared.Pt(13)
                continue
                
        if template_type in ["phu_luc_gia_han", "phu_luc_gia_han_ngan_han"]:
            if "Đơn giá thuê trước đàm phán" in p.text:
                if p._element is not None:
                    p.text = f"- Đơn giá thuê không đổi: {{{{NEW_PRICE}}}} đồng/tháng ( đã bao gồm thuế VAT)\n- Thời gian thuê: đến {{{{END_DATE}}}} ( thêm {extension_years} năm)\n- Chu kỳ thanh toán: 06 tháng/lần vào đầu kỳ"
                    for run in p.runs:
                        run.font.name = "Times New Roman"
                        try: run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                        except Exception: pass
                        run.font.size = docx.shared.Pt(13)
            elif "Đơn giá thuê sau đàm phán" in p.text:
                if p._element is not None:
                    p_element = p._element
                    p_element.getparent().remove(p_element)
                    p._p = p._element = None
                continue

        # Tự động thêm dòng lý do đề xuất trình vượt giá mặt bằng so với quy định vào Tờ trình nếu giá mặt bằng vượt khung (mb_price_pay > mb_raw)
        if mb_price_pay > mb_raw and not getattr(doc, '_already_inserted_mb_overframe_reason', False):
            if "Kính trình Phó Giám đốc" in p.text or "Thời gian áp dụng giá thuê mới" in p.text:
                doc._already_inserted_mb_overframe_reason = True
                try:
                    reason_text = f"- Lý do đề xuất trình vượt giá mặt bằng so với qui định: trạm {site_id} là phục vụ Trạm dừng chân cao tốc Long Thành – Dầu Giây có lưu lượng cao. Các trạm gần nhất cách 1.8km đến 2.3km nên vùng phủ khu vực này rất thưa. Vì vậy, nếu phải di dời hoặc hủy trạm {site_id} sẽ ảnh hưởng đến khách hàng và tốn kém chi phí di dời."
                    p_reason = p.insert_paragraph_before(reason_text)
                    p_reason.style = p.style
                    for run in p_reason.runs:
                        run.font.name = "Times New Roman"
                        try: run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                        except Exception: pass
                        run.font.size = docx.shared.Pt(13)
                except Exception: pass

        # Add extension line to Tờ trình proposal list
        if apply_extension and not getattr(doc, '_already_inserted_proposal_ext', False):
            is_target_p = False
            if "Đơn giá thuê sau đàm phán" in p.text and template_type not in ["phu_luc_gia_han", "phu_luc_gia_han_ngan_han"]:
                is_target_p = True
            elif "Phụ lục này có hiệu lực từ ngày" in p.text and template_type in ["phu_luc_cct_a", "phu_luc_cct"]:
                is_target_p = True
                
            if is_target_p:
                doc._already_inserted_proposal_ext = True
                try:
                    next_p = paragraphs[idx + 1] if (idx + 1) < len(paragraphs) else p
                    p_ext = next_p.insert_paragraph_before(f"gia hạn hợp đồng đến ngày {end_date_str}")
                    p_ext.style = p.style
                    for run in p_ext.runs:
                        run.font.name = "Times New Roman"
                        try: run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                        except Exception: pass
                        run.font.size = docx.shared.Pt(13)
                except Exception: pass

        # General extension clause insertion for any template where apply_extension is True
        if apply_extension and "Điều chỉnh điều 3" in p.text:
            if p._element is not None and not getattr(p, '_already_inserted_term_ext', False):
                p._already_inserted_term_ext = True
                try:
                    p1 = p.insert_paragraph_before("•\tĐiều chỉnh điều 2: Thời hạn cho thuê")
                    for run in p1.runs:
                        run.font.name = "Times New Roman"
                        try: run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                        except Exception: pass
                        run.font.size = docx.shared.Pt(13)
                        run.bold = True
                    p2 = p.insert_paragraph_before(f"Bổ sung thêm khoản\t: gia hạn hợp đồng đến ngày {end_date_str}")
                    for run in p2.runs:
                        run.font.name = "Times New Roman"
                        try: run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                        except Exception: pass
                        run.font.size = docx.shared.Pt(13)
                except Exception: pass
                


        if template_type in ["phu_luc_cct_a", "phu_luc_cct"] and apply_extension:
            if "Phụ lục này có hiệu lực từ ngày" in p.text:
                if p._element is not None and not getattr(p, '_already_inserted_term', False):
                    p._already_inserted_term = True
                    try:
                        p1 = p.insert_paragraph_before(f"Gia hạn thời hạn cho thuê: Bổ sung thêm khoảng thời gian gia hạn từ ngày {start_date_str} đến {end_date_str}")
                        for run in p1.runs:
                            run.font.name = "Times New Roman"
                            try: run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                            except Exception: pass
                            run.font.size = docx.shared.Pt(13)
                    except Exception: pass

        # Xử lý tự động câu chữ và ngày hiệu lực cho dòng "Thời gian áp dụng..." trong Tờ trình
        if "Thời gian áp dụng giá thuê mới" in p.text or "Thời gian áp dụng:" in p.text:
            if not apply_vb1245 or not has_reduction or template_type in ["phu_luc_gia_han", "phu_luc_gia_han_ngan_han"]:
                p.text = f"- Thời gian áp dụng: Kể từ ngày {start_date_str}."
            else:
                p.text = f"- Thời gian áp dụng giá thuê mới: Kể từ ngày {start_date_str}."
            for run in p.runs:
                run.font.name = "Times New Roman"
                try: run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                except Exception: pass
                run.font.size = docx.shared.Pt(13)

        # Xóa trùng lặp 2 dấu gạch ngang "- - " ở đầu đoạn văn nếu có
        if p.text.startswith("- - "):
            p.text = "- " + p.text[4:].strip()
        elif p.text.startswith("-  - "):
            p.text = "- " + p.text[5:].strip()

        text = p.text
        original_text = text
        import re
        if "Giảm từ" in text or "giảm từ" in text:
            # Replace the hardcoded string from the template with dynamic PRICE_PHRASING
            text = re.sub(r"Gi[aả]m từ \{\{OLD_PRICE\}\}.*?\{\{NEW_PRICE_TEXT\}\}\)", "{{PRICE_PHRASING}}", text, flags=re.IGNORECASE)
            
        for tag, rep in replacements.items():
            if tag in text:
                text = text.replace(tag, str(rep))
                
        if text != original_text:
            p.text = text
            if "{{CSHT_LIST" in original_text or "{{ CSHT_LIST" in original_text:
                p.paragraph_format.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = "Times New Roman"
                run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                run.font.size = docx.shared.Pt(13)
                
        bold_triggers = [
            "Thời điểm bắt đầu tính tiền",
            "Giảm trừ số tiền",
            "Một bên là: Ông/Bà",
            "Thông tin tài khoản nhận thanh toán là",
            "Tên tài khoản:",
            "Số tài khoản:",
            "Tại ngân hàng:",
            "Địa chỉ trạm:"
        ]
        signature_triggers = [
            "ĐẠI DIỆN MOBIFONE",
            "ĐẠI DIỆN BÊN THUÊ",
            "ĐẠI DIỆN BÊN CHO THUÊ",
            "XÁC NHẬN CỦA ĐƠN VỊ"
        ]
        if not has_page_broken and any(trigger in p.text.upper() for trigger in signature_triggers):
            p.paragraph_format.page_break_before = True
            has_page_broken = True
            
        if "CỘNG HÒA XÃ HỘI" in p.text.upper() or "CỘNG HOÀ XÃ HỘI" in p.text.upper():
            republic_count += 1
            if republic_count > 1:
                p.paragraph_format.page_break_before = True
            
        if any(trigger in p.text for trigger in bold_triggers) or (owner_name and p.text.strip() == owner_name.strip()):
            for run in p.runs:
                run.bold = True

    for table in doc.tables:
        for row_obj in table.rows:
            for cell in row_obj.cells:
                for p in cell.paragraphs:
                    text = p.text
                    original_text = text
                    for tag, rep in replacements.items():
                        if tag in text:
                            text = text.replace(tag, str(rep))
                            
                    if text != original_text:
                        p.text = text
                        for run in p.runs:
                            run.font.name = "Times New Roman"
                            run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                            run.font.size = docx.shared.Pt(14)
                            
                    if any(trigger in p.text for trigger in bold_triggers) or (owner_name and p.text.strip() == owner_name.strip()):
                        for run in p.runs:
                            run.bold = True

    # 7. Render Payment Table
    pay_table = None
    for table in doc.tables:
        if len(table.rows) > 0:
            first_cell_text = table.rows[0].cells[0].text
            row_texts = [cell.text for cell in table.rows[0].cells]
            if "kỳ" in first_cell_text.lower() or "thanh toán" in first_cell_text.lower() or any("{{PAY_ROW}}" in t or "{{ PAY_ROW }}" in t for t in row_texts):
                pay_table = table
                break
                
    if pay_table is None:
        is_phu_luc = template_type and "phu_luc" in str(template_type).lower()
        if is_phu_luc and len(doc.tables) > 4:
            pay_table = doc.tables[4] # Usually table 4 in Phu Luc template
        elif len(doc.tables) > 8:
            pay_table = doc.tables[8]
            
    if pay_table:
        try:
            pay_table.style = 'Table Grid'
        except Exception:
            pass # Ignore if style doesn't exist
            
        for i, period in enumerate(periods):
            line = f"+ Kỳ {period['no']}: từ ngày {period['start'].strftime('%d/%m/%Y')} đến ngày {period['end'].strftime('%d/%m/%Y')}, Số tiền là: {format_vn_currency(period['amount'])} đồng"
            
            if i == 0 and len(pay_table.rows) > 0 and (pay_table.rows[0].cells[0].text.strip() == "" or "{{PAY_ROW}}" in pay_table.rows[0].cells[0].text or "{{ PAY_ROW }}" in pay_table.rows[0].cells[0].text):
                row_obj = pay_table.rows[0]
            else:
                row_obj = pay_table.add_row()
                
            row_obj.height = docx.shared.Inches(0.3)
            row_obj.height_rule = docx.enum.table.WD_ROW_HEIGHT_RULE.EXACTLY
            
            cell = row_obj.cells[0]
            cell.text = line
            p = cell.paragraphs[0]
            p.paragraph_format.line_spacing_rule = docx.enum.text.WD_LINE_SPACING.SINGLE
            p.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.LEFT
            for run in p.runs:
                run.font.name = "Times New Roman"
                run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                run.font.size = docx.shared.Pt(13)
                
        # Thêm dòng tổng cộng vào cuối bảng pay_table
        if len(periods) > 0:
            total_row = pay_table.add_row()
            total_row.height = docx.shared.Inches(0.3)
            total_row.height_rule = docx.enum.table.WD_ROW_HEIGHT_RULE.EXACTLY
            total_cell = total_row.cells[0]
            total_cell.text = f"Tổng cộng: {format_vn_currency(total_amount)} đồng"
            tp = total_cell.paragraphs[0]
            tp.paragraph_format.line_spacing_rule = docx.enum.text.WD_LINE_SPACING.SINGLE
            tp.alignment = docx.enum.text.WD_ALIGN_PARAGRAPH.RIGHT
            for run in tp.runs:
                run.font.name = "Times New Roman"
                run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
                run.font.size = docx.shared.Pt(13)
                run.bold = True
            
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    output_filename = f"{prefix}_{site_id}.docx"
    output_path = os.path.join(output_dir, output_filename)
    doc.save(output_path)
    return True, output_filename
