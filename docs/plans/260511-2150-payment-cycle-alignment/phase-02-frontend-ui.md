# Phase 02: Frontend UI Update
Status: ⬜ Pending
Dependencies: Phase 01

## Objective
Cập nhật giao diện để hiển thị bảng chu kỳ thanh toán đã được căn chỉnh.

## Requirements
### Functional
- [ ] Import `date-fns` (nếu chưa có) để xử lý ngày tháng đồng bộ với backend.
- [ ] Cập nhật component hiển thị bảng chu kỳ trong `App.tsx`.
- [ ] Hiển thị cảnh báo nếu ngày bắt đầu không phải mùng 01 (Thông báo về việc dồn ngày lẻ).

## Implementation Steps
1. [ ] Cập nhật `frontend/src/utils/siteLogic.ts` để đồng bộ logic tính toán với backend (để preview realtime).
2. [ ] Chỉnh sửa `frontend/src/App.tsx` để render bảng kỳ thanh toán mới.

## Files to Create/Modify
- `frontend/src/utils/siteLogic.ts`
- `frontend/src/App.tsx`

## Test Criteria
- [ ] Người dùng thấy bảng preview khớp với ví dụ trong ảnh hợp đồng mẫu.
