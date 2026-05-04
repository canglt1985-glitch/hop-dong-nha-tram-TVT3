# Phase 03: Validation - DNTP09 Test
Status: ⬜ Pending
Dependencies: Phase 02

## Objective
Kiểm tra thực tế với site DNTP09 để đảm bảo mọi con số đều chính xác.

## Requirements
- [ ] Xuất file Word cho site DNTP09.
- [ ] Kiểm tra Kỳ 1: 01/01/2026 - 30/06/2026.
- [ ] Kiểm tra số tiền Kỳ 1 (đã trừ khấu trừ 3 tháng?).
- [ ] Kiểm tra Kỳ cuối và Tổng cộng.

## Implementation Steps
1. [ ] Chạy `batch_processor.py` cho riêng site DNTP09.
2. [ ] Mở file kết quả (nếu dùng được script đọc text từ docx) hoặc kiểm tra log.
3. [ ] So sánh với tính toán thực tế.

## Files to Create/Modify
- `backend/batch_processor.py` (điều chỉnh limit hoặc filter site)

## Test Criteria
- [ ] Các con số khớp 100% với mong đợi của User.
