# Project Spec: Hệ thống Soạn thảo Phụ lục Hợp đồng BTS

## 1. Tổng quan
Hệ thống hỗ trợ nhân viên quản lý hạ tầng tự động hóa việc lập phụ lục hợp đồng, đảm bảo tính chính xác của dữ liệu địa giới và đơn giá mới.

## 2. Dữ liệu nguồn
- **Danh sách HĐ:** DANH_SACH_HOP_DONG_MAT_BANG_NHA_TRAM_21_04_2026.xlsx
- **Bảng giá:** DS1245 PLHD.xlsx (mẫu đơn giá 1245)
- **Địa chỉ:** TOAN BO DU LIEU_1278_TRAM...xlsx (Địa danh mới)
- **Template:** DNCM02.docx, DNCM11.docx, DNCM24.docx

## 3. Quy tắc cốt lõi
- Khóa chính: Site ID / Mã trạm.
- Gia hạn: Hết hạn < 01/07/2026 -> +5 năm.
- Tài chính: Áp giá từ 01/10/2025, chu kỳ 6 tháng.
- Hiển thị: Gợi ý Guide checklist để giảm rủi ro sai sót dữ liệu.

## 4. Công nghệ
- Core: Python 3.x
- Backend: FastAPI
- Frontend: React + Tailwind CSS
- File processing: pandas, docxtpl
