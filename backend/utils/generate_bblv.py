
import docx
import os
from datetime import datetime
from utils.data_utils import format_date_vn

# Mapping of representatives to their titles
REPRESENTATIVE_MAP = {
    "Lê Thanh Quang": "chuyên viên TVT3",
    "Lê Tân Cảng": "Tổ trưởng TVT3",
    "Trần Đăng Phan": "Chuyên viên TVT3"
}

def format_vn_currency(amount):
    try:
        if amount is None or amount == "": return "0"
        return "{:,.0f}".format(float(amount)).replace(",", ".")
    except Exception:
        return "0"

def parse_date(date_str):
    if not date_str or str(date_str).strip() in ["nan", "None", ""]:
        return None
    formatted = format_date_vn(date_str)
    if formatted:
        try:
            return datetime.strptime(formatted, "%d/%m/%Y")
        except:
            pass
    return None

def calc_khung_gia(site):
    """Tính khung giá VB1245: tổng các hạng mục và làm tròn xuống 50.000"""
    p = site.get("prices_breakdown", {})
    mb = float(p.get("mb", 0) or 0)
    pm = float(p.get("pm", 0) or 0)
    mfd = float(p.get("mfd", 0) or 0)
    cot_rounded = float(p.get("cot_rounded", 0) or 0)
    vhkt = float(p.get("vhkt", 0) or 0)
    total = mb + pm + mfd + cot_rounded + vhkt
    
    return (int(total) // 50000) * 50000


def replace_text_in_paragraph(p, replaces):
    """
    Thay thế văn bản trong paragraph p và định dạng đồng nhất Times New Roman, cỡ 13pt.
    """
    has_replacement = False
    for k in replaces:
        if k in p.text:
            has_replacement = True
            break
            
    if not has_replacement:
        return False
        
    new_text = p.text
    for k, v in replaces.items():
        new_text = new_text.replace(k, str(v))
        
    p.text = ""
    run = p.add_run(new_text)
    run.font.name = "Times New Roman"
    run.font.size = docx.shared.Pt(13)
    from docx.oxml.ns import qn
    run._element.rPr.rFonts.set(qn('w:eastAsia'), "Times New Roman")
    return True

def generate_bblv_document(site_data, representative, output_path, scenario="auto"):
    """
    Tạo Biên bản làm việc dựa trên mẫu templates/BBLV.docx và site_data.
    Các trường cần thay thế:
      - "2501-24/HĐ-MLMN-ĐVTĐN" -> contract_no
      - "23/08/2024" -> contract_date
      - "Diêu Vân Anh" -> owner
      - "30/09/2029" -> end_date
      - "DNDQ51" -> site_id
      - "Lê Tân Cảng" -> representative
      - "Tổ trưởng TVT3" -> representative_title (e.g. Tổ trưởng TVT2)
      - "3.700.000" -> old_price
      - "   0" -> new_price (khung giá VB1245 của trạm)
      - Địa chỉ trong TH1: Thửa đất số 71, tờ bản đồ số 65,ấp 1, xã La Ngà, huyện Định Quán, tỉnh Đồng Nai -> address_old/address_new
      - Ngày hiệu lực:
        + Nếu là CSHT (không thuộc diện MBF): 01/10/2025
        + Nếu là MBF: Ngày kỳ thanh toán tiếp theo: paid_until_date + 1 ngày
    """
    template_path = os.path.join(
        os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 
        "templates", 
        "BBLV.docx"
    )
    if not os.path.exists(template_path):
        raise FileNotFoundError(f"Template BBLV not found at {template_path}")

    doc = docx.Document(template_path)
    
    # Lấy thông số từ trạm
    site_id = site_data.get("site_id", "")
    contract_no = site_data.get("contract_no") or "................................"
    
    # Định dạng ngày của HĐ
    contract_date_raw = site_data.get("contract_date", "")
    contract_date_dt = parse_date(contract_date_raw)
    contract_date = contract_date_dt.strftime("%d/%m/%Y") if contract_date_dt else "......................"
    
    # Định dạng ngày hết hạn
    end_date_raw = site_data.get("end_date", "")
    end_date_dt = parse_date(end_date_raw)
    end_date = end_date_dt.strftime("%d/%m/%Y") if end_date_dt else "......................"

    owner = site_data.get("owner") or "................................"
    
    # Địa chỉ
    address_old = site_data.get("address_old") or site_data.get("contact_addr") or ""
    address_new = site_data.get("address_new") or ""
    address = address_new or address_old or "..........................................................."

    # Đơn giá
    old_price_val = float(site_data.get("old_price") or 0)
    old_price = format_vn_currency(old_price_val)

    # Đơn giá đề xuất (luôn lấy đơn giá khung quy định làm tròn xuống 50.000 để làm việc với chủ nhà)
    new_price_val = calc_khung_gia(site_data)
        
    site_type = str(site_data.get("site_type") or "").upper()
    is_mbf = "MBF" in site_type or "MOBIFONE" in site_type or "MAT" in site_type or "MẶT" in site_type
    
    new_price = format_vn_currency(new_price_val)

    # Người đại diện Bên A
    rep_title = REPRESENTATIVE_MAP.get(representative, "Tổ trưởng")

    # Ngày hiệu lực đơn giá
    site_type = str(site_data.get("site_type") or "").upper()
    is_mbf = "MBF" in site_type or "MOBIFONE" in site_type or "MAT" in site_type or "MẶT" in site_type
    
    if is_mbf:
        # Đối với trạm thuê mặt bằng (Mobifone), áp dụng thời điểm thanh toán tiếp theo theo yêu cầu
        effective_date_str = "kỳ thanh toán tiếp theo"
    else:
        # Dùng ngày hiệu lực cố định 01/10/2025 cho CSHT có sẵn
        effective_date_str = "01/10/2025"

    # Logic xác định nội dung BBLV theo loại template
    bblv_subject = ""
    bblv_proposal = ""
    bblv_reason = ""
    overrides = {}

    if scenario in ["phu_luc_cct_a", "phu_luc_cct", "phu_luc_cct_a_gia_han", "phu_luc_cct_gia_han"]:
        bblv_subject = f"chuyển đổi chủ thể hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng trạm BTS {site_id}"
        if "gia_han" in scenario:
            bblv_subject += " và gia hạn thời gian thuê"
        bblv_proposal = "Đề xuất Quý Chủ trạm hợp tác, chấp thuận chuyển đổi chủ thể Hợp đồng:"
        bblv_reason = "Đảm bảo tính pháp lý do thay đổi từ chủ sở hữu, tiếp tục duy trì hoạt động trạm BTS phục vụ người dân khu vực và mong muốn hợp tác lâu dài."
        overrides["Đơn giá sau khi điều chỉnh giảm:"] = "Đơn giá giữ nguyên/điều chỉnh theo hợp đồng:"
        overrides["Hình thức: ký phụ lục điều chỉnh"] = "Hình thức: ký phụ lục chuyển đổi chủ thể"
        overrides["Đồng ý giảm chi phí thuê mặt bằng, thuê cơ sở hạ tầng (CSHT)"] = "Đồng ý chuyển đổi chủ thể hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng (CSHT)"
        overrides["Không đồng ý giảm chi phí thuê mặt bằng, không bàn giao lại CSHT như đề nghị, chỉ đồng ý giảm ……………………đồng/tháng từ ngày…………………….."] = "Không đồng ý chuyển đổi chủ thể, Ý kiến: ..................................................................."

    elif scenario in ["thanh_ly_ky_lai", "thanh_ly_ky_moi", "ky_moi_hop_dong"]:
        bblv_subject = f"thanh lý và ký lại hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng trạm BTS {site_id}"
        bblv_proposal = "Đề xuất Quý Chủ trạm hợp tác, chấp thuận thanh lý và ký lại hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng:"
        bblv_reason = "Hợp đồng cũ đã hết hiệu lực pháp lý (hoặc cần chuyển đổi pháp nhân), tiếp tục duy trì hoạt động trạm BTS phục vụ và mong muốn hợp tác lâu dài."
        overrides["Đơn giá sau khi điều chỉnh giảm:"] = "Đơn giá ký lại hợp đồng:"
        overrides["Hình thức: ký phụ lục điều chỉnh"] = "Hình thức: thanh lý cũ và ký lại hợp đồng mới"
        overrides["Đồng ý giảm chi phí thuê mặt bằng, thuê cơ sở hạ tầng (CSHT)"] = "Đồng ý ký lại hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng (CSHT) với điều kiện như đề nghị"
        overrides["Không đồng ý giảm chi phí thuê mặt bằng, không bàn giao lại CSHT như đề nghị, chỉ đồng ý giảm ……………………đồng/tháng từ ngày…………………….."] = "Không đồng ý ký lại hợp đồng, Ý kiến: ..................................................................."

    elif scenario in ["phu_luc_giam_gia_gia_han", "phu_luc_giam_gia_gia_han_ngan_han"]:
        bblv_subject = f"giảm chi phí thuê và gia hạn hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng trạm BTS {site_id}"
        bblv_proposal = "Đề xuất Quý Chủ trạm chia sẻ, chấp thuận giảm giá thuê và gia hạn thời gian thuê:"
        bblv_reason = "Tiết giảm chi phí thuê cơ sở hạ tầng theo chủ trương của Tổng Công ty Viễn Thông MobiFone, kết hợp đối soát gia hạn thời gian thuê để hợp tác lâu dài."
        overrides["Hình thức: ký phụ lục điều chỉnh"] = "Hình thức: ký phụ lục giảm giá và gia hạn"

    elif scenario in ["phu_luc_gia_han", "phu_luc_gia_han_ngan_han", "gia_han"]:
        bblv_subject = f"gia hạn thời gian thuê mặt bằng, thuê cơ sở hạ tầng trạm BTS {site_id}"
        bblv_proposal = "Đề xuất Quý Chủ trạm hợp tác, chấp thuận gia hạn thời gian thuê mặt bằng, thuê cơ sở hạ tầng:"
        bblv_reason = "Hợp đồng sắp (hoặc đã) hết hạn, tiếp tục duy trì hoạt động trạm BTS phục vụ người dân khu vực và mong muốn hợp tác lâu dài với Quý Chủ trạm."
        overrides["Đơn giá sau khi điều chỉnh giảm:"] = "Đơn giá thuê trong thời gian gia hạn:"
        overrides["Hình thức: ký phụ lục điều chỉnh"] = "Hình thức: ký phụ lục gia hạn thời gian thuê"
        overrides["Đồng ý giảm chi phí thuê mặt bằng, thuê cơ sở hạ tầng (CSHT)"] = "Đồng ý gia hạn hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng (CSHT)"
        overrides["Không đồng ý giảm chi phí thuê mặt bằng, không bàn giao lại CSHT như đề nghị, chỉ đồng ý giảm ……………………đồng/tháng từ ngày…………………….."] = "Không đồng ý gia hạn hợp đồng, Ý kiến: ..................................................................."

    else:
        # Default fallback to giảm giá or auto based on prices
        is_vuoht_khung = old_price_val > new_price_val
        if is_vuoht_khung or scenario in ["phu_luc_giam_gia", "giam_gia"]:
            bblv_subject = f"giảm chi phí thuê mặt bằng, thuê cơ sở hạ tầng trạm BTS {site_id}"
            bblv_proposal = "Đề xuất Quý Chủ trạm chia sẻ, chấp thuận giảm giá thuê mặt bằng, thuê cơ sở hạ tầng:"
            bblv_reason = "tiết giảm chi phí thuê cơ sở hạ tầng và tối ưu chi phí sản xuất kinh doanh theo chủ trương của Tổng Công ty Viễn Thông MobiFone, cũng như mong muốn hợp tác lâu dài với Quý Chủ trạm."
        else:
            bblv_subject = f"điều chỉnh hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng trạm BTS {site_id}"
            bblv_proposal = "Đề xuất Quý Chủ trạm hợp tác, thống nhất điều chỉnh hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng:"
            bblv_reason = "Cập nhật, điều chỉnh các điều khoản hợp đồng phù hợp với tình hình thực tế để duy trì hợp tác lâu dài."
            overrides["Đơn giá sau khi điều chỉnh giảm:"] = "Đơn giá ký lại hợp đồng:"
            overrides["Hình thức: ký phụ lục điều chỉnh"] = "Hình thức: thanh lý cũ và ký lại hợp đồng mới"
            overrides["Đồng ý giảm chi phí thuê mặt bằng, thuê cơ sở hạ tầng (CSHT)"] = "Đồng ý ký lại hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng (CSHT) với đơn giá mới như đề nghị của bên A"
            overrides["Không đồng ý giảm chi phí thuê mặt bằng, không bàn giao lại CSHT như đề nghị, chỉ đồng ý giảm ……………………đồng/tháng từ ngày…………………….."] = "Không đồng ý ký lại hợp đồng thuê mặt bằng, thuê cơ sở hạ tầng (CSHT) với đơn giá mới như đề nghị của bên A,Ý kiến :"

    # Từ điển thay thế
    replaces = {
        "{contract_no}": contract_no,
        "{contract_date}": contract_date,
        "{owner}": owner,
        "{end_date}": end_date,
        "DNDQ51": site_id,
        "{representative}": representative,
        "{representative_title}": rep_title,
        "{old_price}": old_price,
        "{new_price}": new_price,
        "{effective_date}": effective_date_str,
        "{address}": address,
        "{bblv_subject}": bblv_subject,
        "{bblv_proposal}": bblv_proposal,
        "{bblv_reason}": bblv_reason,
    }

    # Cập nhật các overrides động
    replaces.update(overrides)


    # Thay thế trong bảng
    for table in doc.tables:
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    replace_text_in_paragraph(p, replaces)

    # Thay thế trong tất cả đoạn văn
    for p in doc.paragraphs:
        replace_text_in_paragraph(p, replaces)

    # Lưu kết quả
    doc.save(output_path)
    return output_path
