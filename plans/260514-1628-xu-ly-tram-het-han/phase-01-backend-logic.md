# Phase 01: Cập nhật Backend Logic
Status: ⬜ Pending
Dependencies: N/A

## Objective
Thay đổi logic Backend để hệ thống khi nhận diện được `template_type` truyền lên từ Frontend (dựa vào lựa chọn của user) có thể gán đúng mốc thời gian và template tương ứng. Đặc biệt quan trọng phần Thanh lý ký mới.

## Requirements
### Functional
- [x] Xử lý endpoint `/generate/{site_id}` trong `main.py` và `cloud_document_generator.py`
- [x] Tuỳ chọn 1 (Giảm giá): Giữ nguyên kỳ hạn hợp đồng cũ.
- [x] Tuỳ chọn 2 (Gia hạn giảm giá): Ngày kết thúc (end_date) = Ngày kết thúc hiện tại + 5 năm.
- [x] Tuỳ chọn 3 (Thanh lý ký mới): Tự động chọn file `THANH_LY_KY_LAI_CSHT` / `THANH_LY_KY_LAI_MAT_BANG` mà không cần phát sinh nút bấm trên UI vì UI hiện tại đã chọn được template này. Quan trọng là mốc thời gian phải được set đúng.

## Implementation Steps
1. [x] Rà soát lại code `web_app.py` và `main.py` để tìm vị trí nhận biến date.
2. [x] Inject logic thay thế date dựa theo kết quả đàm phán (nếu user truyền cờ hoặc UI có chỗ select).
3. [x] Đảm bảo tool không hỏng logic báo cáo dư nợ.

## Files to Create/Modify
- `backend/main.py` - Cập nhật logic điều hướng.
- `backend/cloud_document_generator.py` - Chèn logic sinh ngày.

## Test Criteria
- [ ] Gửi request Thanh lý ký lại cho DNCM38, xem file Word có đúng template Không.

---
Next Phase: phase-02-testing.md
