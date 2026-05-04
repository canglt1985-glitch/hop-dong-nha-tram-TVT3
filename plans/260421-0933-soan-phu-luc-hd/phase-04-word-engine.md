# Phase 04: Word Template Engine

## Objective
Tự động điền dữ liệu vào mẫu Word .docx

## Tasks:
- [ ] Phân tích 3 mẫu Word (`DNCM02`, `DNCM11`, `DNCM24`) để xác định các vị trí đặt thẻ (tags).
- [ ] Viết module `docxtpl` để render file Word:
    - Điền thông tin bên thuê/cho thuê.
    - Điền bảng hạng mục đơn giá (với logic tính toán từ Phase 3).
    - Điền các điều khoản gia hạn.
- [ ] Xử lý định dạng số (1.000.000) và ngày tháng (DD/MM/YYYY) trong Word.

## Test Criteria:
- [ ] Xuất file Word mở lên không bị lỗi font, bảng biểu không bị xô lệch.
