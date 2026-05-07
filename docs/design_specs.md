# 🎨 Design Specifications: BTS Contract Automation Dashboard

**Phiên bản:** v1.0.0 (Premium Dark Theme)  
**Tác giả:** Mai (Creative Director - Antigravity)  
**Trạng thái:** Chờ duyệt UI Mockup  

---

## 🎨 1. Hệ thống Màu sắc (Color Palette)

Giao diện sử dụng bảng màu **Premium Dark Mode** với phong cách **Sleek Tech & Glassmorphism** (tương tự như Vercel, Linear, Stripe) để tạo độ chuyên nghiệp, giảm mỏi mắt khi xử lý lượng dữ liệu trạm lớn và tăng tính thẩm mỹ vượt trội.

| Tên màu | Mã Hex | Tỷ lệ sử dụng | Vai trò trong giao diện |
| :--- | :--- | :--- | :--- |
| **Deep Dark Background** | `#0B0F19` | 60% | Nền chính toàn bộ ứng dụng |
| **Surface Card** | `#151D30` | 20% | Nền cho các thẻ panel, bảng biểu, form |
| **Border Slate Glow** | `#263554` | — | Đường viền siêu mảnh (1px) tạo chiều sâu 3D |
| **Vibrant Blue (Primary)**| `#3B82F6` | 10% | Nút hành động, trạng thái "Ký Mới" |
| **Neon Green (Success)** | `#10B981` | 5% | Tiến độ đã hoàn thành, Trạng thái "Đạt đàm phán" |
| **Amber Orange (Warning)**| `#F59E0B` | 5% | Trạng thái "Chờ trình ký", "Gia Hạn" |
| **Coral Red (Failed)** | `#EF4444` | 5% | Đàm phán thất bại, "Thanh lý" |

---

## 📐 2. Bố cục Giao diện (Layout Grid)

Giao diện được chia thành **3 phân vùng trực quan (Split-Screen Grid)**:

```
+-----------------------------------------------------------------------------------+
|  [Logo] BTS Contract Automation Dashboard                             (User Avt)  |
+-----------------------------------------------------------------------------------+
|  [SIDEBAR]     |  [MAIN CONTENT AREA]                                             |
|                |  +------------------------------------------------------------+  |
|  - Tất cả trạm |  |  THẺ THÔNG TIN TRẠM CHỌN (Mã trạm, chủ nhà, sđt, địa chỉ...) |  |
|  - Đạt đàm phán|  +------------------------------------------------------------+  |
|  - Chưa đạt    |                                                                  |
|  - Đã trình ký |  +--------------------------+  +------------------------------+  |
|  - Cần gia hạn |  |  CHỌN LOẠI TEMPLATE      |  |  TIẾN ĐỘ TRÌNH KÝ            |  |
|                |  |  [ ] Phụ lục giảm giá    |  |  [✓] 1. Soạn dự thảo (Draft) |  |
|  [HỖ TRỢ]      |  |  [ ] Phụ lục gia hạn     |  |  [✓] 2. Trình duyệt nội bộ   |  |
|  - Hướng dẫn   |  |  [ ] Thanh lý ký lại     |  |  [ ] 3. Đã ký đóng dấu       |  |
|  - Supabase DB |  |  [ ] Thanh lý ký mới     |  |  [ ] 4. Đã lưu trữ văn thư   |  |
|                |  |  [ ] Hợp đồng ký mới     |  |                              |  |
|                |  +--------------------------+  +------------------------------+  |
|                |                                                                  |
|                |  +------------------------------------------------------------+  |
|                |  |  BẢNG SO SÁNH GIÁ CHI TIẾT (22 hạng mục lẻ & Tổng cộng)     |  |
|                |  |  Hạng mục | Giá hiện tại | Giá 1245 quy định | Giá chốt    |  |
|                |  +------------------------------------------------------------+  |
+-----------------------------------------------------------------------------------+
```

---

## ✨ 3. Thiết kế chi tiết các Component chính

### 3.1. Selector Chọn loại văn bản (Template Type Selector)
*   **Visual Representation:** Thay vì một Dropdown khô khan, chúng ta thiết kế **5 thẻ lựa chọn lớn dạng Grid (Visual Cards)**.
*   **Trạng thái tương tác (Hover/Active states):**
    *   Mỗi thẻ có 1 Icon đặc trưng từ `lucide-react`.
    *   Khi di chuột qua, thẻ nổi nhẹ lên kèm hiệu ứng viền phát sáng (Glow border) theo màu chủ đề.
    *   Khi click chọn, thẻ đổi sang trạng thái active với nền gradient trong suốt và đánh dấu tích xanh neon nổi bật.

### 3.2. Checkbox Tiến độ Trình ký (Status Tracker Card)
*   **Mục tiêu:** Giúp nhân viên nghiệp vụ đánh dấu và theo dõi trạng thái hồ sơ của từng trạm theo thời gian thực.
*   **Các mốc theo dõi:**
    1.  `DRAFT_PREPARED`: Đã soạn xong dự thảo file Word (Hệ thống tự động tích khi người dùng bấm "Xuất file Word").
    2.  `SUBMITTED_FOR_SIGNING`: Đã trình duyệt nội bộ / trình đối tác ký.
    3.  `SIGNED_AND_STAMPED`: Đã ký đóng dấu hoàn tất.
    4.  `ARCHIVED`: Đã lưu trữ văn thư và đồng bộ dữ liệu chốt lên Supabase DB.
*   **UX Detail:** Mỗi bước trình ký có hiệu ứng thanh tiến trình (Progress Bar) chạy song song cực kỳ trực quan.

### 3.3. Dashboard So sánh Đơn giá (Price Metrics & Table)
*   **Thống kê nhanh (Metric Badges):** 
    *   Hiển thị 3 con số tổng cực to ở đầu bảng: **[Giá hiện tại] ➔ [Giá mục tiêu/Quy định 1245] ➔ [Giá chốt thực tế]**.
    *   Kèm theo Badge hiển thị tỷ lệ tiết giảm tự động tính toán (Ví dụ: `▲ Giảm 1,164,000đ/tháng (-19.4%)` màu xanh lá sáng).
*   **Bảng phân rã 22 hạng mục đơn giá lẻ (Expandable Breakdown Table):**
    *   Mặc định chỉ hiển thị các hạng mục có phát sinh chi phí để tránh rối mắt (phòng máy, mặt bằng, cột anten, phòng MFĐ).
    *   Có nút **"Xem đầy đủ 22 hạng mục lẻ 1245"** dạng Accordion. Khi bấm, bảng sẽ trượt xuống mượt mờ (smooth-height animation) hiển thị toàn bộ giá quy định Caps của 22 hạng mục để đối chiếu.

---

## 🚀 4. Gợi ý hoạt động của Giao diện (Interactive Flows)

1.  **Bước 1: Chọn trạm** ở cột Danh sách bên trái (hỗ trợ ô tìm kiếm nhanh đa năng theo Mã trạm hoặc Tên chủ nhà).
2.  **Bước 2: Hệ thống tự động nạp dữ liệu** từ Supabase và hiển thị so sánh đơn giá hiện tại vs đơn giá 1245 lên màn hình chính.
3.  **Bước 3: Chọn Template cần soạn thảo:** Người dùng click vào 1 trong 5 thẻ template (Phụ lục giảm giá, gia hạn, thanh lý ký lại, thanh lý ký mới, ký mới). Hệ thống sẽ tự động chuyển đổi định dạng và nạp đúng bộ thẻ mẫu Word.
4.  **Bước 4: Bấm "Sinh file văn bản"**: Hệ thống xuất file `.docx` siêu tốc, tự động tích xanh bước 1 `[✓] Đã soạn dự thảo`.
5.  **Bước 5: Cập nhật tiến độ**: Khi hồ sơ được duyệt và ký đóng dấu, người dùng chỉ cần tick chọn các bước tiếp theo ngay trên giao diện để hệ thống đồng bộ trạng thái trực tiếp lên Supabase DB giúp cả phòng cùng theo dõi.

---

## 🖼️ 5. Bản vẽ UI Mockup Thiết kế (Mockup Preview)

Dưới đây là hình ảnh bản vẽ thiết kế Premium Dashboard đã được em dựng sẵn. Ảnh đã được lưu thành artifact tại:
`C:\Users\Administrator\.gemini\antigravity\brain\5c3d8abf-dfff-410d-af8d-33d2a5379910\contract_automation_dashboard_mockup_1778042401337.png`
*(Hãy xem và duyệt thiết kế này để em bắt đầu code nhé anh!)*
