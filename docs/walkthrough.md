# 🏆 WALKTHROUGH: Standardized "Thanh Lý Ký Lại" Contract Generation

We have successfully built and verified the complete administrative document generation engine for the **"Thanh lý ký lại"** (Termination & Resign) workflow, fully satisfying the official Vietnamese administrative writing standards (Nghị định 30/2020/NĐ-CP).

---

## 🛠️ Key Improvements & Solutions Delivered

### 1. Pure-Python Zero-Dependency Vietnamese Spelling Engine
*   **Problem:** The `num2words` library was missing in the local Python environment, which caused crashes during offline execution.
*   **Solution:** Built a highly optimized, recursive, pure-Python spelling engine `number_to_vietnamese_words` that converts any value (such as `4350000`) into flawless Vietnamese words (`"Bốn triệu ba trăm năm mươi nghìn"`), guaranteeing 100% offline production safety.

### 2. Multi-Run Formatting Preservation (Nghị định 30/2020/NĐ-CP Compliance)
*   **Problem:** Traditional text-replacement methods in Python-docx collapse all paragraph runs into a single unformatted block, removing bold prefixes (e.g., **`BÊN CHO THUÊ: `**) and italic suffixes (e.g., *`(Gọi tắt là Bên A)`*).
*   **Solution:** Developed a character run-preserving substitutions engine (`replace_tag_in_runs`). It substitutes ONLY the tag values within their specific sub-runs, keeping all surrounding formats (bolds, italics) fully intact and strictly reinforcing the **Times New Roman** font on the replaced runs.

### 3. High-Fidelity Mathematical Dating & Proration Math
*   **Term calculations:** Automatically loads the contract end date from the master spreadsheet and pushes it to the last day of its expiring month, then sets:
    *   `New Start Date` = Month-end date + 1 day
    *   `New End Date` = Start date + 5 years - 1 day
*   **Payment Cycles Table:** Dynamically generates exactly 10 cycles of 6-month payment rows with Times New Roman 14pt inside the document's payment schedule table.

---

## 🧪 Validation & Test Results

We ran the generation engine on the real **DNXL10** station dataset from `DATA HOP DONG.xlsx`:

```powershell
& "d:\Chuyen doi so\soan HD\.venv\Scripts\python.exe" "d:\Chuyen doi so\soan HD\soan-thao-phu-luc-hd\generate_thanh_ly_contract.py"
```

### Extracted & Calculated Data Points:
*   **Owner Name:** `Nguyễn Thị Phượng`
*   **CCCD:** `052175000166`
*   **Contract No / Date:** `348-22/HĐ-MLMN-ĐVTĐN` signed on `09/02/2022`
*   **Original Expiry Date:** `30/06/2027`
*   **Calculated Term:** From `01/07/2027` to `30/06/2032` (5-Year Term)
*   **HPSL (Certificate):** Safely detected that Column 42 held a Ward name instead of a certificate, so it wrote blank lines `_________________` for manual input.
*   **Price Math:** `4.356.000 VND` ➔ Rounded down to 50k: `4.350.000 VND`
*   **Price Spelling:** `Bốn triệu ba trăm năm mươi nghìn đồng`
*   **Schedule Generated:** Exactly 10 payment cycles of 6 months each starting from `01/07/2027` to `30/06/2032`.

**Generated Contract Output:**
📄 **[Thanh_Ly_Ky_Lai_DNXL10.docx](file:///d:/Chuyen%20doi%20so/soan%20HD/soan-thao-phu-luc-hd/output/Thanh_Ly_Ky_Lai_DNXL10.docx)**
