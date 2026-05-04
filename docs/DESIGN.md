# 🎨 DESIGN: Hệ thống Soạn thảo Phụ lục Hợp đồng BTS

Ngày tạo: 2026-04-21
Dựa trên: [project_spec.md](file:///d:/Chuyen%20doi%20so/soan%20HD/soan-thao-phu-luc-hd/docs/specs/project_spec.md)

---

## 1. Cách Lưu Thông Tin (Data Model)

Hệ thống không sử dụng Database trung tâm mà sử dụng **Virtual Data Mapping** từ các file Excel:

- **Bảng Hợp Đồng (Contract):** `MaTram` -> `NgayHetHan`, `DiaChiCu`, `ChuKyThanhToan`.
- **Bảng Đơn Giá (Price):** `MaTram` -> `DonGiaMatBang`, `DonGiaNhaTram`, `TienKhauTru`.
- **Bảng Địa Danh (Address):** `MaTram` -> `XaPhuongMoi`, `QuanHuyenMoi`.

---

## 2. Danh Sách Màn Hình

| # | Tên | Mục đích | Chức năng chính |
|---|-----|----------|-----------------|
| 1 | **Import Dashboard** | Nhập liệu ban đầu | Chọn file, kiểm tra tính hợp lệ của Excel/Word. |
| 2 | **Site List** | Quản lý danh sách | Lọc trạm cần gia hạn, trạm đã duyệt. |
| 3 | **Pre-check Guide** | Kiểm soát rủi ro | So sánh Cũ/Mới, tính khấu trừ tài chính, checklist duyệt. |
| 4 | **Export Studio** | Xuất bản | Chọn template, xuất file hàng loạt, xem log kết quả. |

---

## 3. Luồng Hoạt Động (User Journey)

### 📍 Luồng: Soạn thảo thông thường
1. **Mở App** -> Chọn 3 file Excel và Folder chứa 3 mẫu Word.
2. **Dashboard** -> Hệ thống hiển thị danh sách trạm kèm cảnh báo (Gia hạn/Áp giá 1245).
3. **Review** -> Click vào 1 trạm, app hiện bảng tính toán:
   - Nếu `End Date < 01/07/2026` -> Show `New End Date (+5 years)`.
   - Tính toán `Khấu trừ` = `(Giá mới - Giá cũ) * Số tháng lố từ 01/10/2025`.
4. **Approve** -> Nhấn "Confirm".
5. **Generate** -> Chọn `DNCM02/11/24` -> Xuất file Word.

---

## 4. Checklist Kiểm Tra (Acceptance Criteria)

### 📋 Tính năng: Mapping Dữ liệu
- [ ] Tìm đúng thông tin trạm dựa trên Site ID từ 3 nguồn khác nhau.
- [ ] Xử lý được các trường hợp Mã trạm bị thừa khoảng trắng hoặc sai định dạng chữ hoa/thường.

### 📋 Tính năng: Logic Tài chính & Thời hạn
- [ ] Tự động cộng 5 năm cho các hợp đồng hết hạn trước mốc 01/07/2026.
- [ ] Tính đúng chênh lệch tài chính từ mốc cố định 01/10/2025.
- [ ] Chu kỳ thanh toán mặc định chuyển về 6 tháng.

### 📋 Tính năng: Xuất file Word
- [ ] Điền đúng tags vào file Word mẫu mà không làm hỏng định dạng Table.
- [ ] Format số tiền theo định dạng VNĐ (có dấu chấm phân cách).

---

## 🧪 TEST CASES (Chuẩn bị trước khi code)

### TC-01: Gia hạn hợp đồng
- **Given:** Hợp đồng hết hạn ngày 20/05/2026.
- **When:** Load dữ liệu vào app.
- **Then:** App phải đề xuất ngày hết hạn mới là 20/05/2031.

### TC-02: Tính khấu trừ
- **Given:** Giá cũ 2tr, giá mới 3tr. Đã thanh toán đến 01/01/2026.
- **When:** Tính toán khấu trừ từ 01/10/2025.
- **Then:** Số tiền khấu trừ = (3tr - 2tr) * 3 tháng (10, 11, 12) = 3tr.

---
*Thiết kế bởi Minh - AWF Solution Architect*
