# Phase 01: Backend Date Logic
Status: ⬜ Pending
Dependencies: None

## Objective
Xây dựng hàm xử lý ngày tháng để dồn ngày lẻ vào Kỳ 1 và căn chỉnh ngày kết thúc hợp đồng.

## Requirements
### Functional
- [ ] Viết hàm `get_last_day_of_month(date)`.
- [ ] Viết hàm `calculate_aligned_cycles(start_date, cycle_months, term_years)`.
- [ ] Logic: Kỳ 1 kết thúc cuối tháng, Kỳ 2 bắt đầu mùng 01.
- [ ] Logic: Ngày kết thúc HĐ = Ngày cuối tháng của (Start + Term).

## Implementation Steps
1. [ ] Cập nhật `backend/utils/pricing_utils.py` với các hàm helper về ngày tháng.
2. [ ] Test hàm với các case: tháng 2 năm nhuận, tháng có 30/31 ngày.
3. [ ] Cập nhật API endpoint `/calculate_cycles` (nếu có) hoặc logic trong `/generate`.

## Files to Create/Modify
- `backend/utils/pricing_utils.py` - Thêm logic xử lý ngày tháng.

## Test Criteria
- [ ] Input: 09/04/2026, 6 tháng -> Kỳ 1 kết thúc 31/10/2026, Kỳ 2 bắt đầu 01/11/2026.
- [ ] Input: 09/04/2026, 5 năm -> Kết thúc HĐ 30/04/2031.
