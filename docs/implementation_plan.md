# 📋 IMPLEMENTATION PLAN: Standardized "Thanh Lý Ký Lại" (Termination & Resign) Generation Engine

## 🎯 Goal & Background
This plan designs a robust, compliant generation engine for **"Thanh lý ký lại"** (Termination & Resign) contracts, ensuring absolute alignment with standard Vietnamese administrative guidelines (Nghị định 30/2020/NĐ-CP) and preventing column shifting "gotchas" when importing Excel datasets.

---

## 🔎 Key Compliance & Design Findings

### 1. Administrative Layout Standards (Chuẩn hành chính Việt Nam):
*   **National Motto (Quốc hiệu & Tiêu ngữ):** Font Times New Roman, bold, centered, with standard divider line.
*   **Bold Titles (Tiêu đề in đậm):** Keeps all standard bold text headers intact (e.g., **BIÊN BẢN THANH LÝ**, **HỢP ĐỒNG THUÊ MẶT BẰNG**, **CHÚNG TÔI GỒM**, **ĐIỀU 1**, **BÊN CHO THUÊ...**).
*   **Red Text Replacement:** Dynamically mapping red-colored hardcoded sample text (`EE0000`) into programmatic double-braced tags (`{{START_DATE}}`, `{{END_DATE}}`, `{{CERTIFICATE}}`, `{{LONGITUDE}}`, `{{LATITUDE}}`, etc.) without altering adjacent texts or fonts.
*   **Font Style & Character Format Verification:**
    *   Verified that the original document runs are explicitly styled with **Times New Roman**.
    *   Validated that replacing hardcoded values at the **Run-Level** (instead of replacing the whole paragraph text) preserves multi-run styling (e.g. bold prefixes `BÊN CHO THUÊ: ` and italic suffixes `(Gọi tắt là Bên A)`) perfectly.
    *   All dynamic tags are explicitly set to inherit or enforce **Times New Roman** during character-level substitution.

### 2. Precise Dating Calculations (Thời hạn 5 năm & 10 chu kỳ):
*   **Original End Date (Ngày kết thúc HĐ cũ):** Loaded from index 26.
*   **Prorated Month End:** Pushed to the **last day of the expiring month** (e.g., `12/06/2027` ➔ `30/06/2027`).
*   **New Contract Start Date:** `Start Date = Month End + 1 day` (e.g., `01/07/2027`).
*   **New Contract End Date:** `End Date = Start Date + 5 years - 1 day` (e.g., `30/06/2032`).
*   **10-Period 6-Month Payment Cycle:** Generates exactly 10 schedule entries inside the docx payment table, with each amount = `6 * NEW_PRICE`.

---

## 🛠️ Proposed Changes

We will implement this in a dedicated generator utility to run locally and expose it to the backend.

### 1. [MODIFY] [batch_processor.py](file:///d:/Chuyen%20doi%20so/soan%20HD/soan-thao-phu-luc-hd/backend/batch_processor.py)
*   **Dynamic Column Mapping (DHM):** Scan headers in Row 5 & 6 dynamically to build a robust index map.
*   **Time & Date Processor:** Implement the prorated 5-year mathematical start/end date calculations.
*   **Dynamic Table Builder:** Append exactly 10 cycles of 6-month payment rows into the contract table dynamically.
*   **"Thanh lý ký lại" Writer:** Generate the file from `templates/THANH LY KY LAI_TEMPLATE.docx` to `output/Thanh_Ly_Ky_Lai_[SITE_ID].docx`.

### 2. [MODIFY] [web_app.py](file:///d:/Chuyen%20doi%20so/soan%20HD/soan-thao-phu-luc-hd/backend/web_app.py)
*   Expose an endpoint `/api/generate_thanh_ly` to trigger the generation and return the populated administrative Word document directly.

---

## 🧪 Verification Plan

### Automated Generation Test
1.  Run a test generation script for station `DNXL10` using `DATA HOP DONG.xlsx`.
2.  Verify:
    *   The term starts on `01/01/2026` and ends on `31/12/2030` (or dynamic based on row 26 end date pushed to month-end).
    *   The certificate (`{{CERTIFICATE}}`) resolves to `giấy chứng nhận quyền sở hữu nhà ở... CS 08575...` from Column 42 (Index 42). If empty, outputs `___________`.
    *   Saves the final compliant document to `output/Thanh_Ly_Ky_Lai_DNXL10.docx`.
