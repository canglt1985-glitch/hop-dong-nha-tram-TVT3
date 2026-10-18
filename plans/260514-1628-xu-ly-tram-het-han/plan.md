# Plan: Xử lý logic 3 tuỳ chọn xuất file cho trạm hết hạn
Created: 14/05/2026
Status: 🟡 In Progress

## Overview
Cập nhật logic tạo văn bản cho các trạm hết hạn như DNCM38, dựa vào 3 kết quả đàm phán chính:
1) Giảm giá (không gia hạn) -> `PHU_LUC_GIAM_GIA_...`
2) Gia hạn + Giảm giá -> `PHU_LUC_GIAM_GIA_...` (với nội dung cộng mốc thời gian 5 năm)
3) Thanh lý ký lại -> `THANH_LY_KY_LAI_...`

## Tech Stack
- Frontend: React / Vite
- Backend: FastAPI / Python
- Database: Excel / Google Sheets

## Phases

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 01 | Cập nhật Backend Logic | ⬜ Pending | 0% |
| 02 | Kiểm thử & Xác nhận | ⬜ Pending | 0% |

## Quick Commands
- Start Phase 1: `/code phase-01`
- Check progress: `/next`
- Save context: `/save-brain`
