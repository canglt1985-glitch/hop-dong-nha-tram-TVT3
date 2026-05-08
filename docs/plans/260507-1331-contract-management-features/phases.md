# Phase 01: Setup & Đánh giá hiện trạng
Status: ⬜ Pending

## Objective
Kiểm tra lại code hiện tại sau đợt dọn dẹp, đảm bảo cấu trúc dữ liệu `Site` đã hỗ trợ đầy đủ các cờ (flags) cần thiết cho 3 nhóm tính năng.

## Implementation Steps
1. [ ] Rà soát lại dữ liệu trả về từ API `/api/sites` xem có đủ cờ: `is_expired`, `is_out_of_price_range`, `is_unpaid`.
2. [ ] Rà soát lại code Frontend xem các thẻ báo cáo (StatsCards) đã hiển thị khớp với logic chưa.

---

# Phase 02: Hoàn thiện bộ lọc & Dashboard (Rà soát)
Status: ⬜ Pending

## Objective
Xây dựng giao diện lọc danh sách trạm thông minh và trực quan nhất.

## Implementation Steps
1. [ ] Thêm nút/dropdown lọc theo Tổ VT (VT1, VT2, VT3, VT4, VT5).
2. [ ] Thêm Tab lọc nhanh: "Sắp hết hạn", "Ngoài khung giá", "Cần đàm phán".
3. [ ] Bảng dữ liệu hiển thị rõ ràng các màu cảnh báo (Đỏ = Hết hạn, Vàng = Đang đàm phán, Xanh = Đã xong).

---

# Phase 03: Xử lý sinh File Word tự động (Phụ lục)
Status: ⬜ Pending

## Objective
Cho phép một click chuột để sinh ra file Word Phụ lục/Hợp đồng điền sẵn số liệu.

## Implementation Steps
1. [ ] Củng cố Backend endpoint `/api/generate/{site_id}`: Đảm bảo đọc đúng file Template Word.
2. [ ] Xử lý logic điền biến (Tags) vào Word: `{{ owner_name }}`, `{{ old_price }}`, `{{ new_price }}`...
3. [ ] Frontend có nút "Tải File Word" trên mỗi trạm ở trạng thái "Đã đồng ý giảm giá".

---

# Phase 04: Chốt luồng Thanh toán & Tracking
Status: ⬜ Pending

## Objective
Quản lý chu trình chốt hồ sơ và đẩy đi thanh toán.

## Implementation Steps
1. [ ] Thêm trạng thái "Đã gửi thanh toán" vào Tiến độ (Progress Tracker).
2. [ ] Lọc ra các trạm chưa thanh toán nhưng đã làm xong phụ lục.
3. [ ] Cảnh báo sai lệch thông tin ngân hàng (Chủ tài khoản ≠ Chủ hợp đồng) để chặn thanh toán sai.
