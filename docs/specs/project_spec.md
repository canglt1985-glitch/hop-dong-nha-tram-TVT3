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
- **Tối ưu phân bổ hạng mục đơn giá:**
  - Nếu tổng tiền thuê cả trạm không vượt hạn mức, nhưng hạng mục Mặt bằng bị vượt trần QĐ 02, tiến hành điều chỉnh đưa Mặt bằng về bằng đúng trần QĐ 02 (vượt 0.00%) và chuyển phần chênh lệch sang Cột anten (đảm bảo Cột anten vẫn ≤ trần sau giảm trừ dùng chung). Việc này giúp 100% hạng mục đạt khung (<= 0.00%), tránh phát sinh thủ tục giải trình vượt giá.
- **Thời gian áp dụng đơn giá mới (Gia hạn không ảnh hưởng VB1245):**
  - Trong trường hợp gia hạn hợp đồng mà không ảnh hưởng điều chỉnh giảm giá theo VB1245 (giữ giá cũ / không giảm thêm), thời gian áp dụng đơn giá mới/thời hạn gia hạn được tính **kể từ ngày của chu kỳ thanh toán mới!** (Ví dụ: Kể từ ngày 01/10/2025 như trên tờ trình mẫu DNTP32).
- **Trạm chưa hết khấu hao 5 năm trong năm 2025:**
  - Đối với các trạm chưa đủ 05 năm phát sóng/khấu hao tính đến 2025, việc áp dụng đơn giá mới theo hợp đồng/phụ lục gia hạn sẽ bắt đầu **kể từ ngày hợp đồng mới hoặc kể từ mốc thời gian đủ 05 năm phát sóng** (Ví dụ: Trạm DNCM44 phát sóng từ `01/01/2021`, đủ 05 năm vào `01/01/2026` -> Đơn giá mới áp dụng từ `01/01/2026`).
- Hiển thị: Gợi ý Guide checklist để giảm rủi ro sai sót dữ liệu.

## 4. Công nghệ
- Core: Python 3.x
- Backend: FastAPI
- Frontend: React + Tailwind CSS
- File processing: pandas, docxtpl
