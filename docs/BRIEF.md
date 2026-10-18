# 💡 BRIEF: Luồng xử lý đàm phán trạm hết hạn (Ví dụ: DNCM38)

**Ngày tạo:** 14/05/2026
**Brainstorm cùng:** Kỹ sư / Quản lý trạm

---

## 1. VẤN ĐỀ CẦN GIẢI QUYẾT
Trạm (ví dụ DNCM38) chuẩn bị hết hạn hợp đồng (30/11/2026). Khi đàm phán thành công với chủ nhà, tuỳ thuộc vào thoả thuận sẽ có các phương án thời hạn & giá khác nhau. Cần quy hoạch rõ cách thức hệ thống tự động sinh văn bản (Phụ lục/Hợp đồng) cho từng ngã rẽ này, mà không làm phình to hoặc rối giao diện người dùng.

## 2. GIẢI PHÁP ĐỀ XUẤT
Tận dụng triệt để hệ thống template đã có sẵn và các tuỳ chọn xuất file hiện tại trên giao diện. Giải quyết bài toán bằng cách điều phối đúng luồng dữ liệu vào 3 kịch bản xuất file mà không cần chế thêm nút bấm mới:
1. Áp dụng xuất file loại Giảm Giá.
2. Áp dụng xuất file loại Gia hạn kèm giảm giá.
3. Áp dụng xuất file loại Thanh lý ký lại hợp đồng.

## 3. ĐỐI TƯỢNG SỬ DỤNG
- **Primary:** Nhân viên quản lý trạm / Người trực tiếp xuất hợp đồng, phụ lục.
- **Secondary:** Quản lý đối soát hợp đồng.

## 4. TÍNH NĂNG & KỊCH BẢN (MVP)

### 🚀 MVP (Quy hoạch 3 luồng):
- [ ] **Kịch bản 1 - Chỉ giảm giá:** Chọn xuất file giảm giá. Thời điểm áp dụng giảm giá cho đến đúng ngày hết hạn cũ (30/11/2026).
- [ ] **Kịch bản 2 - Gia hạn & Giảm giá:** Gắn thêm tệp gia hạn. Hệ thống tự động đẩy thêm 5 năm kể từ mốc hết hạn.
- [ ] **Kịch bản 3 - Thanh lý & Ký mới:** Chỉ tạo file Thanh lý ký lại. (Bộ phụ lục giảm giá/kèm theo sẽ sinh riêng). Mức giá mới áp dụng cho trọn thời gian 5 năm của HĐ mới. Tất cả gom lại vào tool hiện tại, người dùng chỉ chọn từ menu đã có (drop-down list/tuỳ chọn có sẵn).

## 5. ƯỚC TÍNH SƠ BỘ
- **Độ phức tạp:** Đơn giản (Chủ yếu là gắn mapping logic đúng biến (variables) về thời gian, ngày tháng vào các template Word đã có sẵn backend).
- **Rủi ro:** Cần handle logic code chuẩn về ngày hết hạn (end_date) giữa HĐ cũ và HĐ mới để tool tính dư nợ không bị nhầm.

## 6. BƯỚC TIẾP THEO
→ Chạy `/plan` để lên thiết kế chi tiết logic code.
