# Changelog - Hệ thống Soạn thảo Phụ lục BTS

## [2026-04-21]
### Added
- **Logic Gia hạn Hợp đồng**: Tự động tính toán chu kỳ gia hạn và chèn vào Tờ trình.
- **Tổng hợp Giá Phức tạp**: Tự động cộng gộp các loại bệ máy (Shelter/Outdoor/Móng) và các loại cột vào các hạng mục chuẩn.
- **Phân tách Chủ thể**: Phân định rõ Site Owner (người ký) và Account Owner (người nhận tiền).

### Fixed
- **Lỗi Hiển thị Tờ trình**: Đảm bảo dòng gia hạn luôn xuất hiện sau dòng đơn giá mới bất kể định dạng Word.
- **Lỗi Format Bằng chữ**: Loại bỏ chữ "Lẻ" không cần thiết trong chuỗi đọc tiền.
- **Lỗi Ngày tháng**: Đồng bộ ngày ký hợp đồng và ngày báo cáo trên toàn văn bản.

### Technical
- Nâng cấp `get_price_info` để quét gộp 11 cột thành phần giá.
- Tối ưu hóa API xuất file với cơ chế `replace_in_paragraph` thông minh hơn.
