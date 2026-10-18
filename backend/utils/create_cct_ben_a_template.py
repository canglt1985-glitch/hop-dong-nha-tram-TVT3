import docx
import os

def create_template():
    source_path = r"d:\Chuyen doi so\soan HD\soan-thao-phu-luc-hd\CCT Ben A.docx"
    dest_path = r"d:\Chuyen doi so\soan HD\soan-thao-phu-luc-hd\templates\PHU_LUC_CHUYEN_CHU_THE_BEN_A.docx"
    
    # Ensure templates directory exists
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    print(f"Loading draft document: {source_path}")
    doc = docx.Document(source_path)
    
    # Mapping of target strings to their standard tag placeholders
    mappings = {
        # Site details
        "DNLK22": "{{ SITE_ID }}",
        "10DN178": "{{ SITE_CODE }}",
        
        # Contract
        "1485-21/HĐ-MLMN-ĐVTĐN": "{{ CONTRACT_NO }}",
        "02/07/2021": "{{ CONTRACT_DATE }}",
        "Thửa đất số 11, tờ bản đồ số 04, phường Xuân Trung, thị xã Long Khánh, tỉnh Đồng Nai": "{{ LAND_ADDRESS }}",
        
        # Land title and death certificates
        "trích lục khai tử số 646/2025/TLKT-BS ngày 03/11/2025": "{{ ATTACHMENT_DEATH_CERT }}",
        "đơn đề nghị chuyển tên của bà Nguyễn Ngọc Loan ngày 05/12/2025": "{{ ATTACHMENT_DESIRE_LETTER }}",
        "chứng nhận quyền sử dụng số AP398343 ngày 02/12/2009 và Hợp đồng thuê một phần quyền sử dụng đất ngày 29/11/2026 tại Văn phòng Công chứng Nguyễn Hữu Hiếu giữa Ông/ Bà Nguyễn Phước Đại – Thi Bích Loan và Bà Nguyễn Ngọc Loan": "{{ ATTACHMENT_LAND_CERT }}",
        
        # Landlord - Old owner
        "Ông Nguyễn Hùng": "{{ OWNER_OLD_NAME }}",
        "Nguyễn Hùng": "{{ OWNER_OLD_NAME }}",
        "95A Nguyễn Du, P. Xuân An, TX. Long Khánh, Đồng Nai": "{{ OWNER_OLD_ADDRESS }}",
        "0916 66 88 99": "{{ OWNER_OLD_PHONE }}",
        "Số 075068004670 cấp ngày 19/08/2022": "{{ OWNER_OLD_CCCD }}",
        "654 704 060 007 713": "{{ OWNER_OLD_ACCOUNT_NO }}",
        "VIB_ CN Long Khánh, Đồng Nai": "{{ OWNER_OLD_BANK }}",
        
        # Landlord - New owner
        "Bà Nguyễn Ngọc Loan": "{{ OWNER_NEW_NAME }}",
        "Nguyễn Ngọc Loan": "{{ OWNER_NEW_NAME }}",
        "69 Nguyễn Du, phường Long Khánh, tỉnh Đồng Nai": "{{ OWNER_NEW_ADDRESS }}",
        "0919 656 667": "{{ OWNER_NEW_PHONE }}",
        "075177009288 cấp ngày 19/08/2022 tại Cục Cảnh sát QLHC về TTXH": "{{ OWNER_NEW_CCCD }}",
        "5906205448798": "{{ OWNER_NEW_ACCOUNT_NO }}",
        "Agribank": "{{ OWNER_NEW_BANK }}",
        
        # Effective date
        "01/02/2026": "{{ EFFECTIVE_DATE }}",
    }
    
    # Sort keys by length in descending order to avoid partial replacement (e.g. replacing 'Nguyen Hung' before 'Ong Nguyen Hung')
    sorted_keys = sorted(mappings.keys(), key=len, reverse=True)
    
    def replace_text_in_paragraph(p):
        # We replace directly in the run text to retain formatting
        for key in sorted_keys:
            replacement = mappings[key]
            # Replace in runs
            for run in p.runs:
                if key in run.text:
                    run.text = run.text.replace(key, replacement)
            
            # Double check: if target string was split across runs, 
            # the run-by-run check might miss it. 
            # In that case, we fall back to a full paragraph replacement.
            # However, to avoid collapsing formatting, we check if the key is still in paragraph.text
            if key in p.text:
                # Resolve spanned items by concatenating runs
                # But since it's a template generation, let's warn and replace directly if needed
                p_text_before = p.text
                # Let's attempt safe merge: if only 1 run, just replace
                if len(p.runs) == 1:
                    p.runs[0].text = p.runs[0].text.replace(key, replacement)
                else:
                    # If spanned, we will perform a basic substitution on the first run and clear others
                    # this is acceptable when creating templates.
                    full_text = p.text.replace(key, replacement)
                    p.text = "" # clears runs
                    p.add_run(full_text)
                    print(f"  Warning: Spanned string '{key}' collapsed runs in paragraph.")

    # 1. Process paragraphs
    for idx, p in enumerate(doc.paragraphs):
        replace_text_in_paragraph(p)
            
    # 2. Process tables
    for t_idx, table in enumerate(doc.tables):
        for row in table.rows:
            for cell in row.cells:
                for p in cell.paragraphs:
                    replace_text_in_paragraph(p)
                    
    doc.save(dest_path)
    print(f"Success! Final template generated at: {dest_path}")

if __name__ == "__main__":
    create_template()
