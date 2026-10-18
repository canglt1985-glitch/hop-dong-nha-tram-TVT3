# 💡 BRIEF: Tính năng xuất Phụ Lục Chuyển Chủ Thể hàng loạt

**Ngày tạo:** 18/05/2026
**Workflow:** `/brainstorm`

---

## 1. VẤN ĐỀ CẦN GIẢI QUYẾT
Hiện tại, việc làm Phụ lục Chuyển chủ thể cho các trạm lấy từ mẫu (như DNCM36) đang phải làm thủ công. Quá trình điền tên chủ cũ, chủ mới, số hợp đồng, giá thuê... mất nhiều thời gian và dễ sai sót.

## 2. GIẢI PHÁP ĐỀ XUẤT
Mở rộng hệ thống hiện tại để hỗ trợ XUẤT HÀNG LOẠT (Bulk Export) Phụ lục Chuyển Chủ Thể. 
- Chỉ cần nhập danh sách mã trạm (Site IDs) vào một ô input.
- Hệ thống sẽ tự động quét data từ Google Sheets.
- Sử dụng template chuẩn (được gắn tag từ file DNCM36).
- Nhả ra một file ZIP chứa toàn bộ Phụ lục của các trạm vừa nhập.

## 3. TÍNH NĂNG (FEATURE SCOPE)

### 🚀 MVP (Bắt buộc có):
- [ ] Tool quét file Word mẫu (DNCM36.docx), tự động nhận diện chữ ĐỎ và thay bằng tag (như `{{CHU_CU}}`, `{{CHU_MOI}}`).
- [ ] Giao diện (UI) mới: Có khu vực "Xuất hàng loạt", cho phép copy-paste danh sách mã trạm (dạng text hoặc excel dán vào).
- [ ] Nút chọn loại Phụ lục: "Phụ lục chuyển chủ thể".
- [ ] Log thông báo thành công / lỗi (VD: "Trạm DNXX01 thiếu thông tin ngân hàng chủ mới").

### 🎁 Phase 2 (Làm sau):
- [ ] Tải lên file Excel danh sách trạm thay vì copy-paste.
- [ ] Xuất gom chung thành 1 file Word duy nhất thay vì file ZIP chứa nhiều file (nếu cần in hàng loạt dễ hơn).

## 4. BƯỚC TIẾP THEO
Em đang chạy lệnh quét phân tích chữ đỏ trên file DNCM36 của anh. Sau khi quét xong em sẽ confirm lại danh sách tag thiết yếu. Nếu anh đồng ý với phương án này, ta sẽ chuyển qua `/plan` để chốt database và luồng xử lý!
