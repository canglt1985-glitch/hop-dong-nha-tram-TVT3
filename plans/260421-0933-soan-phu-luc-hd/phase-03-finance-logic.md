# Phase 03: Finance & Date Logic

## Objective
Hiện thực hóa các quy tắc nghiệp vụ phức tạp về thời hạn và tiền tệ.

## Tasks:
- [ ] Logic Gia hạn: Kiểm tra nếu `Hết hạn < 01/07/2026` -> Tự động tính `Ngày hết hạn mới = Ngày hiện tại + 5 năm` (hoặc theo quy định cụ thể).
- [ ] Logic Tính khấu trừ (Deduction Calculation):
    - Tính số ngày từ 01/10/2025 đến ngày thanh toán gần nhất (nếu có).
    - Tính chênh lệch (Đơn giá mới - Đơn giá cũ).
    - Tính tổng tiền cần khấu trừ/truy thu.
- [ ] Chu kỳ thanh toán: Gán mặc định 6 tháng.

## Test Criteria:
- [ ] Một trạm hết hạn 2024 phải được gia hạn đến 2029.
- [ ] Tính đúng số tiền chênh lệch từ mốc 01/10/2025.
