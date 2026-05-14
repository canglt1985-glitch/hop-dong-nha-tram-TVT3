# Phase 02: Refactor Code Generator Backend
Status: ⬜ Pending
Dependencies: Phase 01

## Objective
Gỡ bỏ các logic dán cứng (như replace "30/09/2028" hay dò tìm "Tổng cộng:") trong file `cloud_document_generator.py`, giúp hàm sinh Word chạy mượt mà theo chuẩn Tag.

## Requirements
### Functional
- [ ] Xóa logic `if "30/09/2028" in text:` và thay thế `text.replace(...)`.
- [ ] Xóa logic kiểm tra chữ `"Tổng cộng:"` và thay thế bằng việc inject trực tiếp giá trị vào thẻ `{{TOTAL_AMOUNT}}` ngay trong đoạn nội dung tương ứng.
- [ ] Đồng bộ lại `replacements` map: đảm bảo nó bao quát cả VHKT và MFĐ cho tất cả các loại template.

## Implementation Steps
1. [ ] Mở file `backend/cloud_document_generator.py`.
2. [ ] Tìm vòng lặp `for p in doc.paragraphs` và dọn dẹp các logic thay thế thủ công.
3. [ ] Tối ưu hóa hàm `replace_tag_in_runs` nếu cần để không làm hỏng format khi chèn Tag.
4. [ ] Cập nhật bảng dictionary `replacements` cho gọn gàng.

## Files to Create/Modify
- `backend/cloud_document_generator.py`

---
Next Phase: Phase 03 (Testing)
