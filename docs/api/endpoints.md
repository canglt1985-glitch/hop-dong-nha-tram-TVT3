# API Documentation

Ngày cập nhật: 2026-05-19
Base URL: `http://localhost:5173/api` (Frontend Proxy) -> `http://localhost:8000` (Backend)

---

## 📡 Các Hệ Thống Endpoint Cốt Lõi

### GET /api/sites
Tải danh sách các trạm viễn thông từ cơ sở dữ liệu Google Sheets cache.

**Response (200):**
```json
[
  { "site_id": "DNCM36", "owner": "Nguyễn Văn A", "old_price": 5000000, "new_price": 4500000, ... }
]
```

### POST /api/progress
Lưu lại tiến độ đàm phán, ghi nhận kết quả và giá cuối cùng vào tracking JSON log.

---

## 📄 Sinh Biểu Mẫu (Document Generators)

### POST /api/generate-document
Sinh đơn lẻ một file Word (Thanh lý, Phụ lục, v.v...) dựa theo cấu hình trạng thái của trạm trong đàm phán.

**Request:**
```json
{
  "site_id": "DNLK60",
  "template_type": "phu_luc_giam_gia",
  "bank_info": { ... }
}
```

### POST /api/generate-bulk-cct
Sinh hàng loạt Phụ lục hợp đồng Chuyển Chủ Thể lấy từ 1 mảng danh sách các mã trạm đầu vào. Cung cấp file `.zip` nén toàn bộ tài liệu lại để tải xuống một lần trả lại `filename`.

**Request:**
```json
{
  "site_ids": ["DNCM36", "DNLK60", "DNTN24"]
}
```

**Response (200):**
```json
{
  "success": true,
  "filename": "Bulk_PhuLuc_CCT_20260519_xxxx.zip",
  "count": 3,
  "errors": []
}
```

### GET /api/download/{filename}
Tải file đã sinh (Word hoặc ZIP) về máy Local.

---

## 📈 Xuất Báo Cáo
### POST /api/export-progress
Lấy toàn bộ lịch sử đàm phán sinh thành một tệp danh sách file báo cáo tình trạng toàn bộ các trạm.
