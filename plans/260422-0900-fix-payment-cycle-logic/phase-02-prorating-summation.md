# Phase 02: Logic Refactor - Pro-rating & Summation
Status: ⬜ Pending
Dependencies: Phase 01

## Objective
Hiện thực hóa việc tính tiền theo tỉ lệ cho các kỳ ngắn và tự động tính Tổng cộng.

## Requirements
- [x] Tính `amt` dựa trên số tháng thực tế của kỳ thay vì fix cứng `new_price * 6`.
- [x] Tính tổng tích lũy `total_amount` của tất cả các kỳ được tạo ra.
- [x] Cập nhật template hoặc replacement của {{TOTAL_PAYMENT}} (nếu cần).

## Implementation Steps
1. [x] Cập nhật vòng lặp `while` trong `batch_processor.py` để tính `amt` chính xác.
2. [x] Thêm biến `total_contract_sum` để cộng dồn các kỳ.
3. [x] Chèn dòng "Tổng cộng" vào cuối bảng hoặc cập nhật placeholder.

## Files to Create/Modify
- `backend/batch_processor.py`

## Test Criteria
- [ ] Kỳ cuối của DNTP09 (tháng 12/2026) số tiền phải là `new_price / 6 * 1`.
- [ ] Tổng cộng hiển thị trong văn bản phải bằng tổng các Kỳ cộng lại.
