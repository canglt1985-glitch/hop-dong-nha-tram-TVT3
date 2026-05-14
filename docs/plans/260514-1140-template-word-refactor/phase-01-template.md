# Phase 01: Chuẩn hóa File Template Word
Status: ⬜ Pending
Dependencies: None

## Objective
Thay đổi nội dung 4 file template `.docx` chuẩn, loại bỏ các chữ được gõ cứng và điền các Tag còn thiếu (như VHKT, MFĐ, DEDUCTION_TEXT) để xử lý mọi loại trạm mà không bị lỗi thiếu thông tin.

## Requirements
### Functional
- [ ] Trong tất cả các file `THANH_LY_KY_LAI`, tìm đoạn có chứa `30/09/2028` và thay thế thành `{{END_DATE}}`.
- [ ] Đảm bảo bảng biểu của `PHU_LUC_GIAM_GIA_CSHT` có các tag liên quan đến VHKT (Vận hành khai thác).
- [ ] Đảm bảo bảng biểu của `PHU_LUC_GIAM_GIA_MAT_BANG` có các tag liên quan đến Máy phát điện (MFĐ).
- [ ] Chèn tag `{{DEDUCTION_TEXT}}` vào các file `THANH_LY_KY_LAI` ở phần điều khoản thanh toán (để tự động xuất câu giảm trừ nếu có).

## Implementation Steps
1. [ ] Viết một script Python đơn giản (tạm thời) sử dụng thư viện `python-docx` để tự động mở 4 template, thay thế `30/09/2028` bằng `{{END_DATE}}`.
2. [ ] Hoặc sử dụng cách ghi đè trực tiếp XML của DOCX để chỉnh sửa, nhưng do file DOCX là nhị phân, dùng một script xử lý là an toàn nhất.
3. [ ] Xóa file rác `thanh ly ky lai hd.docx`.

## Files to Create/Modify
- `templates/PHU_LUC_GIAM_GIA_CSHT.docx`
- `templates/PHU_LUC_GIAM_GIA_MAT_BANG.docx`
- `templates/THANH_LY_KY_LAI_CSHT.docx`
- `templates/THANH_LY_KY_LAI_MAT_BANG.docx`
- Script hỗ trợ: `patch_templates.py`

---
Next Phase: Phase 02 (Refactor Backend)
