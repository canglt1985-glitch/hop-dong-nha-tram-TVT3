# 🎨 TECHNICAL DESIGN: Extensible BTS Contract Automation Frontend

## 💡 TRIẾT LÝ THIẾT KẾ: "Khung Giao Diện Mở Rộng (Extensible Template Framework)"

Chào anh! Em là **Minh**, Kiến trúc sư giải pháp. Để đáp ứng định hướng phát triển lâu dài của anh — giúp hệ thống không chỉ chạy tốt mẫu "Thanh lý ký lại" hiện tại mà còn dễ dàng tích hợp thêm các mẫu khác (Giảm giá, Gia hạn, Ký mới...) trong tương lai mà **không cần viết lại code giao diện** — em đã thiết kế một kiến trúc Frontend dạng **"Cấu hình hóa (Configuration-Driven)"**.

Thay vì viết code riêng cho từng mẫu, giao diện sẽ tự động dựng khung dựa trên một file cấu hình đăng ký. Khi anh muốn thêm 1 mẫu mới, anh chỉ cần định nghĩa thông tin mẫu đó vào danh sách cấu hình, giao diện sẽ tự sinh thẻ chọn, biểu tượng, và gọi đúng đường dẫn API tương ứng!

---

## 📊 PHẦN 1: Cách Lưu Trữ & Đồng Bộ Thông Tin (Local Progress Storage)

Để theo dõi tiến độ trình ký của từng trạm mà **chưa cần cài đặt cơ sở dữ liệu phức tạp (như Supabase)**, chúng ta sẽ sử dụng bộ nhớ đệm trình duyệt **`localStorage`** kết hợp với đồng bộ tệp động **`progress_tracker.json`** dưới backend.

```
┌────────────────────────────────────────────────────────┐
│ 👤 TRÌNH DUYỆT (Local Storage)                         │
│ Lưu trữ tạm thời tiến độ tick chọn của người dùng.      │
└──────────────────────────┬─────────────────────────────┘
                           │
                           ▼ Đồng bộ qua API cục bộ
┌────────────────────────────────────────────────────────┐
│ 📁 BACKEND (progress_tracker.json)                      │
│ Lưu trữ bền vững, không mất khi dọn cache trình duyệt.  │
└────────────────────────────────────────────────────────┘
```

### Cấu trúc thông tin tiến độ (State Schema):
```typescript
interface SiteProgress {
  selected_template: string; // 'giam_gia' | 'gia_han' | 'thanh_ly_ky_lai' | ...
  progress: {
    draft_prepared: boolean;     // 🟢 Bước 1: Đã soạn dự thảo
    submitted_internal: boolean; // 🟡 Bước 2: Đã trình ký nội bộ
    signed_and_stamped: boolean; // 🔵 Bước 3: Đã ký đóng dấu
    archived_doc: boolean;       // 🟣 Bước 4: Đã lưu trữ văn thư
  };
  last_updated: string;
}
```

---

## 📱 PHẦN 2: Bố Cục Trang & Các Khối Giao Diện (UI Layout Grid)

Giao diện sẽ sử dụng phong cách **Premium Dark Theme** (bảng màu Sleek Space Black & Electric Blue) tạo cảm giác cực kỳ công nghệ và dịu mắt khi thao tác lâu với số liệu.

```
+-----------------------------------------------------------------------------------------+
│  [Logo] BTS Contract Automation Dashboard v2.0 (Premium Black)              (Admin Avt) │
+-----------------------------------------------------------------------------------------+
│  [SIDEBAR]         │  [MAIN CONTENT AREA]                                               │
│  Tìm kiếm trạm...  │  ┌──────────────────────────────────────────────────────────────┐  │
│  [ ] Bộ lọc nhanh  │  │ 👤 THẺ TRẠM ĐANG CHỌN: DNXL10                                │  │
│                    │  │ - Chủ nhà: Nguyễn Thị Phượng  - SĐT: 0937 386 789             │  │
│  - DNXL10 (Đã xong)│  │ - Số HĐ gốc: 348-22           - Ngày hết hạn: 30/06/2027     │  │
│  - BPBL11 (Chờ ký) │  └──────────────────────────────────────────────────────────────┘  │
│  - PTPTA8 (Cần gia)│  ┌──────────────────────────────────────────────────────────────┐  │
│  - XLK12  (Mới)    │  │ 📋 CHỌN LOẠI VĂN BẢN CẦN SOẠN THẢO (TEMPLATE SELECTOR)       │  │
│                    │  │ [ Thẻ Giảm giá ]  [ Thẻ Gia hạn ]  [ Thẻ Thanh lý ký lại 🌟 ] │  │
│                    │  │ [ Thẻ Ký mới ]    [ Thẻ Thanh lý ký mới ]                    │  │
│                    │  └──────────────────────────────────────────────────────────────┘  │
│                    │  ┌──────────────────────────────┬───────────────────────────────┐  │
│                    │  │ 📈 ĐƠN GIÁ ĐỐI CHIẾU         │ 🟢 TIẾN ĐỘ TRÌNH KÝ           │  │
│                    │  │ - Hiện tại: 5,500,000 đ      │ [✓] 1. Soạn dự thảo (Draft)   │  │
│                    │  │ - Mục tiêu 1245: 4,356,000 đ │ [ ] 2. Trình duyệt nội bộ     │  │
│                    │  │ - Giá chốt mới: 4,350,000 đ  │ [ ] 3. Đã ký đóng dấu         │  │
│                    │  │                              │ [ ] 4. Đã lưu trữ văn thư     │  │
│                    │  └──────────────────────────────┴───────────────────────────────┘  │
│                    │  ┌──────────────────────────────────────────────────────────────┐  │
│                    │  │ ⚙️ BẢNG CHI TIẾT 22 HẠNG MỤC LẺ QUY ĐỊNH 1245                 │  │
│                    │  │ (Có nút Expandable: Click để trượt xuống xem chi tiết)       │  │
│                    │  └──────────────────────────────────────────────────────────────┘  │
+-----------------------------------------------------------------------------------------+
```

### Các Khối Màn Hình (Components Tree):
1.  **`SidebarList`:** Chứa ô tìm kiếm đa năng (mã trạm, chủ nhà, SĐT) + Bộ lọc thông minh (Còn hạn/Cần gia hạn; Chưa soạn/Đã trình ký).
2.  **`TemplateGrid` (Extensible Framework):** Dựng 5 ô chọn mẫu văn bản. Thẻ nào đã sẵn sàng sẽ sáng viền xanh, thẻ nào đang phát triển sẽ mờ đi (Disabled) kèm tag "Coming Soon".
3.  **`ProgressStepper`:** Trục tiến độ 4 bước nằm cạnh khối so sánh giá. Người dùng click trực tiếp vào vòng tròn tiến độ để cập nhật trạng thái, đi kèm với **Thanh tiến trình (Progress Bar) chạy mượt mà**.
4.  **`BreakdownTable`:** Bảng so sánh 22 hạng mục đơn giá. Có hiệu ứng thu gọn mặc định, bấm "Xem tất cả" để trượt êm ái xuống dưới hiển thị đầy đủ.

---

## 🚶 PHẦN 3: Luồng Hoạt Động (User Journey)

Hành trình của anh khi sử dụng phần mềm sẽ cực kỳ đơn giản và nhanh gọn:

```
[BƯỚC 1: Tìm & Chọn trạm]
     │
     ▼
[BƯỚC 2: Xem các chỉ số giá ➔ Chọn Mẫu "Thanh lý ký lại"] (Giao diện hiển thị nút màu xanh nổi bật)
     │
     ▼
[BƯỚC 3: Click "SOẠN THẢO VĂN BẢN"]
     │
     ├─► Trình duyệt tải ngay file Word .docx sạch sẽ về thư mục Download
     └─► Tiến độ tự động tích xanh bước 1: 🟢 [✓] Đã soạn dự thảo
     
[BƯỚC 4: Người dùng tự cập nhật bước tiếp theo]
     └─► Click chọn "Trình duyệt nội bộ" ➔ Hệ thống lưu ngay trạng thái không sợ mất.
```

---

## ✅ PHẦN 4: Quy Tắc Kiểm Tra Chất Lượng (Acceptance Criteria)

Giao diện Frontend được nghiệm thu hoàn thành khi đạt các tiêu chuẩn sau:

### 1. Tính tương thích & Co giãn (Responsive & Extensible):
*   [ ] Khi thay đổi cấu hình danh sách mẫu văn bản, giao diện tự động vẽ thêm/bớt thẻ chọn tương ứng mà không lỗi.
*   [ ] Hoạt động trơn tru trên mọi độ phân giải màn hình (máy tính bảng, laptop, màn hình lớn).

### 2. Trải nghiệm người dùng (Premium UX & Micro-Animations):
*   [ ] Thao tác chuyển đổi giữa các trạm phản hồi tức thì (dưới 100ms).
*   [ ] Khi bấm nút "Xem đầy đủ 22 hạng mục lẻ", bảng so sánh trượt xuống mượt mà bằng hiệu ứng CSS transitions, không bị khựng đột ngột.
*   [ ] Các thẻ chọn mẫu văn bản có hiệu ứng phóng to nhẹ (Hover Scale) và phát sáng viền mờ (Glow Borders) khi di chuột qua.

---

## 🧪 PHẦN 5: Các Bài Kiểm Thử Chuẩn Bị Trước (Test Cases)

Chúng ta viết trước 3 kịch bản kiểm tra để áp dụng vào giai đoạn code:

### 🧪 TC-01: Bộ lọc tìm kiếm đa năng
*   **Given:** Danh sách có trạm `DNXL10` (Chủ nhà: Nguyễn Thị Phượng) và `BPBL11` (Chủ nhà: Lê Văn A).
*   **When:** Người dùng gõ `"Phượng"` hoặc `"0937"` hoặc `"DNXL10"` vào ô tìm kiếm.
*   **Then:** Hệ thống lọc ra đúng dòng trạm `DNXL10` và ẩn trạm `BPBL11`.

### 🧪 TC-02: Nhớ trạng thái tiến độ qua F5
*   **Given:** Trạm `DNXL10` đang có tiến độ Bước 1 (Đã soạn dự thảo).
*   **When:** Người dùng click tích chọn Bước 2 (Đã trình duyệt nội bộ) rồi bấm F5 tải lại trang.
*   **Then:** Giao diện vẫn hiển thị dấu tích xanh cho cả Bước 1 và Bước 2 của trạm `DNXL10`.

---

Anh thấy bản thiết kế giao diện theo hướng mở rộng này đã đúng ý anh chưa ạ? Em có cần tinh chỉnh hay thêm khối chức năng nào nữa không anh?
Để chuyển sang xây dựng ngay giao diện tuyệt đẹp này, anh có thể duyệt bản vẽ thiết kế bằng cách phản hồi hoặc gõ `/code` anh nhé!
