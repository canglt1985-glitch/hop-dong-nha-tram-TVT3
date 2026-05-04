# Phase 02: Data Mapping Engine

## Objective
Xây dựng module đọc và liên kết dữ liệu từ 3 file Excel nguồn.

## Tasks:
- [ ] Viết script đọc file "Danh sách hợp đồng": Trích xuất Mã trạm, Ngày hết hạn.
- [ ] Viết script đọc file "DS1245 PLHD": Lấy đơn giá chi tiết từng hạng mục theo Mã trạm.
- [ ] Viết script đọc file "TOAN BO DU LIEU": Lấy thông tin Xã/Phường chuẩn mới.
- [ ] Xây dựng hàm Merge dữ liệu dựa trên Mã trạm (Site ID) làm khóa chính.

## Test Criteria:
- [ ] Nhập 1 mã trạm, trả về đầy đủ: Địa chỉ mới, Đơn giá cũ, Đơn giá mới, Ngày hết hạn.
