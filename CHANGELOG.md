# Changelog
 
## [2026-05-25 - Đồng bộ Biên bản (BBLV) & Hoàn thiện giao diện]
### Added
- **Đồng hành BBLV cho toàn bộ tệp mẫu**: API backend hiện đã tự động sinh kèm tệp đồng hành `BBLV_{site_id}.docx` đi kèm khi người dùng xuất bất kỳ loại mẫu hợp đồng/phụ lục nào, thay vì chỉ giới hạn ở mẫu thanh lý.
- **Sửa hiển thị VHKT và tổng tiền trên UI**: Sửa lỗi giao diện hiển thị thiếu trường VHKT/Bảo vệ và tính tổng bị lệch trên panel ghim Hạng mục giá thuê (yêu cầu) tại giao diện React (`App.tsx`).
- **Quy chuẩn Người Đại diện & Chức danh Bên A**:
  - Lê Tân Cảng (Mặc định): *"Tổ trưởng TVT3"*
  - Lê Thanh Quang: *"chuyên viên TVT3"*
  - Trần Đăng Phan: *"Chuyên viên TVT3"*

### Changed
- **Chống cộng lặp VHKT**: Tích hợp điều kiện loại trừ: chỉ tự động cộng dồn 600K guard fee MobiFone trong biên bản nếu trường dữ liệu excel thô của trạm chưa khai báo trường `vhkt` độc lập.
- **Đơn giản hóa đơn giá BBLV**: Tối giản định dạng giá xuất ra trong biên bản thành chuỗi phẳng (e.g. `3.000.000 đồng/ tháng`) loại bỏ ngoặc giải thích chi tiết theo mong muốn của người dùng.

### Technical
- Cập nhật định nghĩa TypeScript interface `Site` bổ sung trường `vhkt?: number` trong `prices_breakdown`.
- Viết kịch bản kiểm định tích hợp tự động toàn diện `verify_vhkts_and_all_templates.py` kiểm tra chuỗi giá trị và đại diện.

## [2026-05-14 - Phiên chiều]
### Added
- **Pytest Infrastructure**: Tích hợp `pytest` để tự động hóa Unit Test cho backend, cấu hình `pytest.ini`.
- **Template Standardization**: Chèn tag `{{END_DATE}}` thay cho text cứng `30/09/2028`, và thêm `{{DEDUCTION_TEXT}}` vào các hợp đồng Thanh lý.

### Changed
- **Backend Clean-up**: Gỡ bỏ logic "hack" dò text cứng trong `cloud_document_generator.py` để code mượt và ổn định hơn.
- **Dọn dẹp mã nguồn**: Chuyển các file debug scripts cũ vào `scratch/backend_debug_scripts/`.

### Fixed
- Khắc phục lỗi format template và cảnh báo linting trên Frontend.
- Loại bỏ file rác `thanh ly ky lai hd.docx`.

## [2026-05-11 - Phiên chiều/tối]
### Added
- **Chuẩn hóa Ngày kết thúc**: Tất cả hợp đồng/phụ lục gia hạn 5 năm nay luôn kết thúc vào **ngày cuối cùng của tháng** (Ví dụ: 09/04/2026 -> 30/04/2031).
- **Logic Kỳ 1 Thông minh**: Nếu bắt đầu ngày 1, Kỳ 1 tròn 6 tháng. Nếu bắt đầu ngày lẻ, Kỳ 1 = Phần ngày lẻ + 6 tháng trọn vẹn. Đảm bảo các kỳ sau luôn bắt đầu từ ngày mùng 1.
- **Tích hợp Hồ sơ pháp lý**: Trích xuất dữ liệu từ cột 42 Master và gắn tự động vào tag `{{CERTIFICATE}}` / `{{LEGAL_DOCS}}`.
- **Ngắt trang tự động**: Tự động chèn Page Break trước phần ký tên trong file Word để văn bản trình bày đẹp hơn.

### Fixed
- **Lỗi Nghịch đảo Ngày**: Sửa lỗi ngày kết thúc hiển thị trước ngày bắt đầu trong file bản thảo (Phu_Luc).
- **Lỗi Trắng trang Frontend**: Khắc phục lỗi thiếu biểu tượng `Calendar` và cải thiện hàm parse ngày tháng linh hoạt hơn.
- **Hiển thị Bảng Thanh toán**: Tăng độ rõ nét cho bảng preview chu kỳ trên giao diện web.

## [2026-05-11 - Phiên sáng]
### Added
- Thêm 6 loại văn bản hợp đồng chi tiết (Giảm giá, Gia hạn, Gia hạn & Giảm giá, Thanh lý ký lại, v.v.).
- Tính năng "Smart Match Filter" cho bộ lọc MBF để nhận diện trạm MOBIFONE.
- Logic tự động tính ngày gia hạn: Ngày bắt đầu = Ngày kết thúc cũ + 1, thời hạn 5 năm.

### Changed
- Cập nhật Tùy chọn 2 (Gia hạn thời gian): Sử dụng template PHU_LUC_GIAM_GIA, giữ nguyên giá cũ, ẩn căn cứ pháp lý.
- Vá (Patch) các file Word template PHU_LUC_GIAM_GIA để hỗ trợ thẻ {{START_DATE}} và {{END_DATE}}.

### Fixed
- Lỗi lọc trạm MBF không ra kết quả khi dữ liệu là MOBIFONE.
- Lỗi ngày mặc định 01/10/2025 bị ghim cứng trong văn bản gia hạn.

## [2026-05-09]
### Added
- Tích hợp hạng mục VHKT (600.000đ) vào bảng tính giá và template Word.
- Tự động lấy dữ liệu "Hồ sơ pháp lý" (Căn cứ) từ sheet Master.
- Phân luồng thông minh: Trạm MBF mặc định Gia hạn, Trạm khác mặc định Thanh lý ký lại.
- Bộ lọc dropdown template trong giao diện tự động ẩn các biểu mẫu không phù hợp với loại trạm.
- Tích hợp cấu trúc dữ liệu hợp đồng:
  ```json
  "contract_logic": {
    "types": [
      { "id": "phu_luc_giam_gia", "description": "Điều chỉnh đơn giá theo VB1245, ngày mặc định 01/10/2025" },
      { "id": "phu_luc_gia_han", "description": "Gia hạn 5 năm, giữ nguyên giá cũ, ngày bắt đầu = ngày cũ + 1" },
      { "id": "phu_luc_giam_gia_gia_han", "description": "Vừa giảm giá vừa gia hạn 5 năm" },
      { "id": "thanh_ly_ky_lai", "description": "Thanh lý ký lại 5 năm theo chuẩn" }
    ],
    "mbf_logic": {
      "filter_name": "MBF",
      "data_name": "MOBIFONE",
      "template_suffix": "_MAT_BANG.docx"
    },
    "csht_logic": {
      "template_suffix": "_CSHT.docx",
      "hardcoded_items": "Fixed equipment, generator, and antenna descriptions"
    }
  },
  "api_endpoints": [
    { "path": "/api/generate-document", "method": "POST", "params": ["site_id", "template_type"] }
  ]
  ```

### Fixed
- Lỗi lệch hàng định dạng trong mục CSHT (Ghim cứng mô tả tiêu chuẩn).
- Lỗi không nhận giá đàm phán thủ công khi xuất file.
- Lỗi hiển thị trống phần "Căn cứ vào..." khi chưa có hồ sơ pháp lý (thay bằng dòng chấm chấm).

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
