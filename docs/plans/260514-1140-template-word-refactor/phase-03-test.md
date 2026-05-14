# Phase 03: Testing & Cleanup
Status: ⬜ Pending
Dependencies: Phase 02

## Objective
Chạy thử hệ thống sinh Word để đảm bảo các file sau khi sửa template và refactor code vẫn hoạt động hoàn hảo, sinh ra file đúng ngày tháng và không mất format.

## Implementation Steps
1. [ ] Gọi hàm sinh Word với một mẫu dữ liệu CSHT và một mẫu dữ liệu MẶT BẰNG thông qua test api.
2. [ ] Mở và kiểm tra các file xuất ra tại thư mục `output/`.
3. [ ] Xác nhận thông tin Tổng tiền, Ngày kết thúc và Câu giảm trừ đều được điền đúng.
4. [ ] Dọn dẹp script `patch_templates.py` đã dùng ở Phase 01.

## Test Criteria
- File xuất ra mở được bình thường, không bị corrupt.
- Không còn sót chữ "30/09/2028".
- Định dạng in đậm chữ ký/tên chủ nhà được giữ nguyên.
