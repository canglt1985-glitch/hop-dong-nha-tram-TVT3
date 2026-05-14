# Plan: Cải tiến Template Word & Script Sinh Word
Created: 2026-05-14T11:40
Status: 🟡 In Progress

## Overview
Dọn dẹp và chuẩn hóa 4 template Word (`PHU_LUC_GIAM_GIA_...` và `THANH_LY_KY_LAI_...`) để thay thế các text gõ cứng bằng thẻ chuẩn (ví dụ: đổi `30/09/2028` thành `{{END_DATE}}`). Đồng thời tối ưu code trong file `cloud_document_generator.py` để loại bỏ các đoạn xử lý "hack", giúp hệ thống hoạt động ổn định và chính xác với mọi trạm.

## Tech Stack
- Document Processing: `python-docx`
- File format: `.docx`

## Phases

| Phase | Name | Status | Progress |
|-------|------|--------|----------|
| 01 | Chuẩn hóa File Template Word | ✅ Complete | 100% |
| 02 | Refactor Code Generator Backend | ✅ Complete | 100% |
| 03 | Testing & Cleanup | ✅ Complete | 100% |

## Quick Commands
- Bắt đầu Phase 1: `/code phase-01`
- Xem tiến độ: `/next`
- Lưu ngữ cảnh: `/save-brain`
