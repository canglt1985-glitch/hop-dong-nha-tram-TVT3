# 🎨 SYSTEM DESIGN: Excel-Based BTS Contract Automation System

**Kiến trúc sư phần mềm:** Minh (Solution Architect - Antigravity)  
**Phiên bản:** v2.0.0 (Offline-First / Local Excel Architecture)  
**Trạng thái:** Thiết kế chi tiết phục vụ lập trình  

---

## 💡 TRIẾT LÝ KIẾN TRÚC: "Offline-First & Local Excel Engine"

Theo đúng mong muốn của anh, hệ thống sẽ **chạy offline hoàn toàn trên máy tính cá nhân**, sử dụng trực tiếp hai file Excel hiện hữu làm "Cơ sở dữ liệu". Cách tiếp cận này giúp anh kiểm soát dữ liệu 100%, bảo mật tuyệt đối, không phụ thuộc vào mạng internet hay chi phí đám mây, và cực kỳ dễ bảo trì.

Để thay thế cho cơ sở dữ liệu Supabase mà vẫn giữ được tính năng **Theo dõi tiến độ trình ký (Status Checkboxes)**, chúng ta sẽ thiết kế một bộ nhớ đệm JSON phẳng (**`progress_tracker.json`**) lưu cục bộ tại thư mục backend.

---

## 📊 PHẦN 1: Cách Lưu Trữ & Đồng Bộ Thông Tin (Local Data Architecture)

Hệ thống lưu trữ thông tin dựa trên cơ chế gộp 3 nguồn dữ liệu tĩnh và động:

```
┌────────────────────────────────────────────────────────────────────────┐
│ 📁 LOCAL STORAGE SYSTEM (Bộ nhớ cục bộ)                                │
│                                                                        │
│ 1. [DATA HOP DONG.xlsx] (File tĩnh)                                    │
│    └── Thông tin chủ nhà, số hợp đồng, tài khoản ngân hàng, chu kỳ...  │
│                                                                        │
│ 2. [MBF DNa_BC_VB 1245.xlsx] (File tĩnh)                              │
│    └── Đơn giá quy định 1245 (22 hạng mục lẻ), đơn giá đàm phán chốt. │
│                                                                        │
│ 3. [progress_tracker.json] (File ghi động - CẬP NHẬT THEO THỜI GIAN THỰC)│
│    └── Lưu mã trạm (ma_tram), loại template đã chọn, bước trình ký.   │
└──────────────────────────────────┬─────────────────────────────────────┘
                                   │
                                   ▼ [Gộp dữ liệu qua Python pandas]
┌────────────────────────────────────────────────────────────────────────┐
│ 🧠 IN-MEMORY UNIFIED CACHE (Dữ liệu gộp trên RAM)                      │
│    └── Trả về JSON tích hợp đầy đủ cho React Frontend hiển thị         │
└────────────────────────────────────────────────────────────────────────┘
```

### Chi tiết cấu trúc File ghi động `progress_tracker.json`:
```json
{
  "BPBL11": {
    "selected_template": "phu_luc_giam_gia",
    "progress": {
      "draft_prepared": true,
      "submitted": true,
      "signed": false,
      "archived": false
    },
    "last_updated": "2026-05-06T13:40:00Z"
  }
}
```

---

## 📊 PHẦN 1.1: Đặc tả ánh xạ dữ liệu "Thanh lý ký lại" (Data Mapping Spec)

Để nạp dữ liệu chính xác cho biểu mẫu [THANH LY KY LAI_TEMPLATE.docx](file:///d:/Chuyen%20doi%20so/soan%20HD/soan-thao-phu-luc-hd/templates/THANH%20LY%20KY%20LAI_TEMPLATE.docx), hệ thống sử dụng bảng đối chiếu 0-indexed từ file `DATA HOP DONG.xlsx` như sau:

| Thẻ Tag Word | Cột Excel (Tên cột thực tế) | Index (0-based) | Ghi chú & Logic xử lý |
|---|---|---|---|
| `{{SITE_ID}}` | Mã trạm | `1` | Mã nhận diện trạm (Ví dụ: `DNXL10`) |
| `{{OWNER_NAME}}` | Chủ thể hợp đồng | `16` | Tên chủ trạm / chủ nhà đặt trạm |
| `{{PHONE}}` | Số điện thoại chủ nhà | `18` | Điện thoại liên hệ chủ nhà |
| `{{CONTACT_ADDR}}` | Địa chỉ liên hệ | `17` | Địa chỉ thường trú/liên hệ của chủ nhà |
| `{{CONTRACT_NO}}` | Số HĐ | `24` | Số hợp đồng thuê gốc |
| `{{CONTRACT_DATE}}` | Ngày ký HĐ | `25` | Ngày ký hợp đồng gốc (Định dạng: `dd/mm/yyyy`) |
| `{{ADDRESS_OLD}}` | Địa chỉ đặt trạm | `35` | Giữ nguyên văn địa chỉ gốc bao gồm cả số thửa, số tờ bản đồ. |
| `{{CERTIFICATE}}` | HPSL (Hồ sơ pháp lý) | `42` | **Cột mới tự bổ sung**. Nếu rỗng, xuất dòng trống `____________________` để điền tay. |
| `{{ACCOUNT_OWNER}}` | Chủ tài khoản | `87` | Tên chủ tài khoản nhận tiền |
| `{{ACCOUNT_NO}}` | Số tài khoản | `88` | Số tài khoản ngân hàng nhận tiền |
| `{{BANK_NAME}}` | Ngân hàng + Chi nhánh | `89`, `90` | Ghép chuỗi: `[Ngân hàng] - [Chi nhánh]` |

### 📅 Logic toán học thời gian (Thời hạn 5 năm & Kỳ thanh toán 6 tháng):
1.  **Ngày bắt đầu mới:** Ngày tiếp theo sau ngày kết thúc hợp đồng gốc (Cột index 26: `Ngày kết thúc HĐ`). Ngày kết thúc cũ được ép về ngày cuối tháng của tháng hết hạn.
    *   *Ví dụ:* `original_end` = `12/06/2027` ➔ Tròn tháng = `30/06/2027` ➔ Ngày bắt đầu mới = `01/07/2027`.
2.  **Ngày kết thúc mới:** `Start Date + 5 năm - 1 ngày`. (Ví dụ: `30/06/2032`).
3.  **Bảng thanh toán `{{PAY_ROW}}`:** Tự động chia thành 10 dòng kỳ hạn liên tiếp (Chu kỳ thanh toán: 06 tháng), số tiền mỗi kỳ = `6 * đơn giá chốt 1245`.

---

## 📱 PHẦN 2: Các Trang & Component Trên Giao Diện React mới

Ứng dụng React mới sẽ là một bảng điều khiển **Premium Dashboard** được chia thành các phân mảnh giao diện (React Components) độc lập và có khả năng tái sử dụng cao:

### 1. `SidebarStationList` (Danh sách trạm bên trái)
*   **Mục đích:** Hiển thị danh sách 360 trạm kèm theo bộ tìm kiếm nhanh và bộ lọc nhanh trạng thái.
*   **Dữ liệu:** `site_id`, `owner`, `end_date`, `ext_status` (Cần gia hạn/Còn hạn).

### 2. `StationDetailHeader` (Thẻ tổng quan thông tin trạm)
*   **Mục đích:** Hiển thị chi tiết định danh pháp lý của trạm được chọn (Chủ nhà, Số điện thoại, Số HĐ, Địa chỉ cũ, Địa chỉ mới, Thông tin tài khoản ngân hàng).

### 3. `TemplateWorkflowSelector` (Khối chọn loại phụ lục)
*   **Mục đích:** Cung cấp 5 thẻ trực quan (Visual Cards) tương ứng với 5 loại văn bản:
    1.  *Phụ lục giảm giá* (Mẫu `MASTER_TEMPLATE_VFINAL.docx` - Phân hệ Giảm giá)
    2.  *Phụ lục gia hạn* (Mẫu `MASTER_TEMPLATE_VFINAL.docx` - Phân hệ Gia hạn)
    3.  *Thanh lý ký lại* (Mẫu `thanh ly ky lai hd.docx`)
    4.  *Thanh lý ký mới* (Mẫu `thanh ly ky moi hd.docx`)
    5.  *Hợp đồng ký mới* (Mẫu `hop dong ky moi hd.docx`)

### 4. `ProgressTrackerCard` (Theo dõi tiến độ trình ký)
*   **Mục đích:** Hiển thị checklist 4 bước trình ký. Cho phép người dùng click để cập nhật tiến độ. Tiến độ này sẽ được gọi API cập nhật ngay vào `progress_tracker.json`.

### 5. `PriceComparisonDashboard` (Bảng so sánh đơn giá 22 hạng mục)
*   **Mục đích:** So sánh trực quan đơn giá: **[Hiện tại] ➔ [Mục tiêu/Quy định 1245] ➔ [Chốt thực tế]**.
*   **UX Detail:** Mặc định rút gọn, hỗ trợ nút bấm mở rộng hiển thị đầy đủ 22 hạng mục lẻ.

---

## 🚶 PHẦN 3: Luồng Hoạt Động (User Journey)

Hành trình xử lý một hồ sơ trạm tiêu chuẩn sẽ diễn ra như sau:

```
[Mở app] ➔ [Chọn trạm BPBL11] ➔ [Xem bảng giá so sánh]
                                        │
                                        ▼
[Click chọn thẻ "Thanh lý ký lại"] ➔ [Bấm "Soạn thảo hồ sơ"]
                                        │
                                        ▼ (Tự động tải file Word về máy)
[Checklist bước 1 "Đã soạn dự thảo" tự động tích xanh 🟢]
                                        │
                                        ▼ (Người dùng mang hồ sơ trình ký)
[Tick thủ công "Đã trình duyệt nội bộ" ➔ Đồng bộ ngay vào JSON]
```

---

## ✅ PHẦN 4: Quy Tắc Kiểm Tra (Acceptance Criteria)

Tính năng **Quản lý & Soạn thảo Phụ lục Excel-Based** được coi là hoàn thành khi đáp ứng các tiêu chuẩn sau:

### 1. Tiêu chuẩn Đọc & Gộp dữ liệu:
*   [ ] Đọc chuẩn xác 360 trạm từ `DATA HOP DONG.xlsx` mà không bị giật lag (sử dụng in-memory pandas cache).
*   [ ] Ghép đúng mã trạm với đơn giá đàm phán tương ứng tại file `MBF DNa_BC_VB 1245.xlsx`.
*   [ ] Nạp được thông tin tiến độ từ file `progress_tracker.json` lên màn hình mà không bị mất dấu khi tắt/bật lại server.

### 2. Tiêu chuẩn Soạn thảo văn bản:
*   [ ] Khi chọn mẫu "Phụ lục giảm giá", hệ thống gán đúng các biến giá chốt dồn dư (`{{P_MB}}`, `{{P_PM}}`...) vào template.
*   [ ] Khi chọn mẫu "Thanh lý ký lại", hệ thống chuyển đổi và nạp dữ liệu vào file `thanh ly ky lai hd.docx`.
*   [ ] Xuất file `.docx` thành công, lưu vào thư mục `output/` kèm tên file chuẩn hóa: `Phu_Luc_[MA_TRAM]_[NGAY_XUAT].docx`.

### 3. Tiêu chuẩn Giao diện & Tiến độ:
*   [ ] Click cập nhật tiến độ (ví dụ bước 2 `submitted` = true), dữ liệu lập tức lưu xuống file JSON. F5 tải lại trang tiến độ vẫn được giữ nguyên.
*   [ ] Bảng đơn giá format chuẩn đơn vị tiền tệ Việt Nam (Ví dụ: `1.500.000 đ`).

---

## 🧪 PHẦN 5: Bài Kiểm Thử Thiết Kế (Test Cases Design)

Để đảm bảo code viết ra chuẩn xác ngay từ dòng đầu tiên, chúng ta thiết kế sẵn các bài thi thử sau:

#### 🧪 TC-01: Happy Path - Đồng bộ tiến độ trình ký cục bộ
*   **Given:** Server Flask đang chạy, file `progress_tracker.json` chưa có thông tin trạm `BPBL11`.
*   **When:** Trên giao diện React, người dùng chọn trạm `BPBL11`, chọn template `Thanh lý ký lại` và tích chọn bước 2 `Đã trình duyệt nội bộ`.
*   **Then:**
    *   Hệ thống gửi request POST `/api/progress` thành công.
    *   Kiểm tra file `progress_tracker.json` thấy sinh ra bản ghi của `BPBL11` với trạng thái lưu đúng bước 2.
    *   Bấm F5 trình duyệt, trạm `BPBL11` vẫn hiển thị trạng thái tích xanh bước 2 và ghi nhận template đã chọn là `Thanh lý ký lại`.

#### 🧪 TC-02: Edge Case - Excel đang bị mở bởi ứng dụng khác (Excel Lock)
*   **Given:** File `DATA HOP DONG.xlsx` đang được anh mở bằng Microsoft Excel trên Windows (gây ra tình trạng khóa file ghi đọc).
*   **When:** Khởi động Flask Server hoặc gọi API tải danh sách trạm.
*   **Then:**
    *   Python không bị crash hoặc văng lỗi.
    *   Hệ thống sử dụng cơ chế đọc an toàn hoặc bắt ngoại lệ và hiển thị thông báo nhẹ nhàng cho người dùng: *"File Excel đang được mở ở ứng dụng khác, hệ thống đang dùng bản sao tạm thời để hiển thị"*.

---

*Thiết kế bởi AWF 2.1 - Design Phase*
