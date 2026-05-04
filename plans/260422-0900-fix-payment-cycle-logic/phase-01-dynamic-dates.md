# Phase 01: Logic Refactor - Dynamic Dates
Status: ⬜ Pending
Dependencies: None

## Objective
Thay đổi logic lấy ngày bắt đầu `start_date` từ giá trị fix cứng sang việc đọc từ file Excel (Cột 29 trong Master).

## Requirements
- [x] Trích xuất ngày bắt đầu từ chuỗi "01/01/2026 - 30/06/2026" (lấy phần đầu).
- [x] Xử lý trường hợp Cột 29 trống hoặc sai định dạng (fallback về ngày mặc định hợp lý).
- [x] Cập nhật logic tính `deduction_val` dựa trên khoảng cách từ 01/10/2025 đến ngày bắt đầu chu kỳ mới.

## Implementation Steps
1. [x] Chỉnh sửa `batch_processor.py`: Thêm hàm helper `parse_cycle_start`.
2. [x] Cập nhật `process_site`: Thay thế `datetime(2025, 12, 1)` bằng ngày lấy từ Cột 29.
3. [x] Cập nhật logic tính `months_overpaid` trong `finance_service.py` hoặc trực tiếp trong `batch_processor.py`.

## Files to Create/Modify
- `backend/batch_processor.py`
- `backend/finance_service.py`

## Test Criteria
- [ ] Site DNTP09 phải bắt đầu từ 01/01/2026.
- [ ] Số tháng khấu trừ cho DNTP09 phải là 3 (10, 11, 12/2025).
