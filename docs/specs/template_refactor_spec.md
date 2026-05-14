# Cấu Trúc Tổng Quan: Template Word Refactor
**Mục tiêu:** Sửa các lỗi tiềm ẩn khi sinh file Word từ dữ liệu trên Backend.

## 1. Executive Summary
Hệ thống hiện tại đang gặp một số "nợ kỹ thuật" do người dùng chỉnh sửa template Word nhưng điền hardcode dữ liệu (như ngày `30/09/2028` hay dòng `"Tổng cộng:"`). Code backend buộc phải thích nghi bằng cách dò chuỗi. Kế hoạch này sẽ chuẩn hóa template sử dụng biến `{{...}}` (Jinja-style tags) và lược bỏ code "hack" trong hệ thống.

## 2. Các điểm mù (Hidden Logic) đã phát hiện
- File `THANH_LY_KY_LAI_...` thiếu `{{DEDUCTION_TEXT}}`. Nếu không thêm, khách hàng có tiền cấn trừ sẽ không được báo cáo.
- File CSHT thiếu Tag liên quan đến VHKT. File MẶT BẰNG thiếu Tag liên quan đến Máy phát điện (MFĐ).
- File nháp `thanh ly ky lai hd.docx` nằm lẫn trong template, gây rủi ro nạp sai.

## 3. Kiến Trúc Sửa Đổi
- **Templates**: Chèn thêm `{{END_DATE}}`, `{{DEDUCTION_TEXT}}`, `{{TOTAL_AMOUNT}}`.
- **Backend (cloud_document_generator)**:
  - Vòng lặp Paragraphs sẽ chỉ replace theo Dict map, không có if logic "30/09/2028".
  - Code gọn nhẹ hơn, giảm thiểu lỗi format (font Times New Roman).

## 4. Build Checklist
- [ ] Template 1: `PHU_LUC_GIAM_GIA_CSHT.docx`
- [ ] Template 2: `PHU_LUC_GIAM_GIA_MAT_BANG.docx`
- [ ] Template 3: `THANH_LY_KY_LAI_CSHT.docx`
- [ ] Template 4: `THANH_LY_KY_LAI_MAT_BANG.docx`
- [ ] Refactor Code: `backend/cloud_document_generator.py`
