# Phase 02: Kiểm thử & Xác nhận
Status: ⬜ Pending

## Objective
Đảm bảo cả 3 tuỳ chọn đều xuất ra nội dung hợp lệ về ngày tháng, số tiền. Không ảnh hưởng đến các site không thuộc diện sắp hết hạn.

## Requirements
### Testing
- [x] Test xuất file với option 1 (DNCM38) -> Check file `.docx` xem `end_date` có đúng 30/11/2026 không, không có +5 năm.
- [x] Test xuất file với option 2 (DNCM38) -> Check file `.docx` xem `end_date` có cộng thêm 5 năm không.
- [x] Test xuất file với option 3 (DNCM38) -> Check API mapping đúng data cột B bên sheet `DATA HOP DONG`.

## Implementation Steps
1. [x] Gọi API test gen doc từ script python
2. [x] Dùng `docx` parser để check xem nội dung file output chứa đoạn `thời hạn` đúng như đặc tả.
3. [x] Hoàn tất log session.
