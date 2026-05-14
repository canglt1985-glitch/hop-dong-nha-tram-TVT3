# 💡 BRIEF: Manual Price Breakdown & Logic Refinement

**Ngày tạo:** 2026-05-11
**Brainstorm cùng:** canglt1985

---

## 1. VẤN ĐỀ CẦN GIẢI QUYẾT
- Dữ liệu đơn giá từ Google Sheets/Excel đôi khi bị cũ hoặc sai lệch hạng mục (Mặt bằng, MPĐ, Cột anten...).
- Hiện tại app chỉ cho nhập "Tổng đơn giá chốt", khiến các hạng mục con trong file Word bị tính toán sai dựa trên data cũ.
- Người dùng muốn nhập tay trực tiếp 4 hạng mục chính để kiểm soát hoàn toàn con số trong hợp đồng.
- **Mới:** Kỳ thanh toán hiện tại bị lẻ ngày (ví dụ bắt đầu từ 09/04), gây khó khăn cho kế toán theo dõi dòng tiền theo tháng tròn.
- **Mới:** Ngày kết thúc hợp đồng cần được chuẩn hóa về cuối tháng của năm kết thúc để đồng bộ với chu kỳ thanh toán.

## 2. GIẢI PHÁP ĐỀ XUẤT
- Thêm Panel **"Phân rã đơn giá thủ công"** trong phần cập nhật số liệu.
- Áp dụng logic làm tròn 50k tự động và dồn tiền vào mục "Mặt bằng" để khớp tổng giá chốt.
- **Logic Chu kỳ thanh toán (Option A):**
    - **Kỳ 1:** Dồn tất cả ngày lẻ vào kỳ đầu tiên. Kỳ 1 sẽ kết thúc vào ngày cuối cùng (30/31) của tháng thứ N (N là chu kỳ, ví dụ 6 tháng).
    - **Kỳ 2 trở đi:** Bắt đầu từ ngày 01 của tháng kế tiếp để đảm bảo tròn tháng.
- **Logic Ngày kết thúc:** Ngày kết thúc hợp đồng = Ngày cuối cùng (30/31) của tháng kết thúc (Start Date + Term Months).
- **Quy tắc làm tròn:** Chỉ làm tròn ở **Đơn giá** (Unit Price). Phần **Thành tiền** (Total Amount) của kỳ lẻ cứ tính chính xác đến số thập phân (số lẻ).

## 3. ĐỐI TƯỢNG SỬ DỤNG
- **Primary:** Tổ đàm phán (cần chốt số liệu chính xác để in hợp đồng).

## 4. TÍNH NĂNG

### 🚀 MVP (Bắt buộc có):
- [ ] **Giao diện nhập liệu:** 4 ô nhập (Mặt bằng, MPĐ, Cột anten, Giảm trừ).
- [ ] **Auto-calc Total:** Tự động tính tổng khi nhập các hạng mục.
- [ ] **Smart Rounding:** Tự động làm tròn tổng xuống nấc 50,000đ (VD: 3.956.000 -> 3.950.000).
- [ ] **Balance Logic:** Tự động điều chỉnh mục "Mặt bằng" sau khi làm tròn để Tổng khớp tuyệt đối.
- [ ] **End-of-Month Alignment:**
    - [ ] Tính toán Kỳ 1 kết thúc vào cuối tháng.
    - [ ] Tính toán Kỳ 2+ bắt đầu từ ngày 01.
    - [ ] Tự động xác định ngày kết thúc hợp đồng là cuối tháng (VD: 09/04/2026 -> 5 năm -> 30/04/2031).
- [ ] **Persistence:** Lưu breakdown vào `progress_tracker.json`.

### 🎁 Phase 2 (Làm sau):
- [ ] **Template Mapping:** Tự động điền các con số này vào các thẻ `{{P_MB}}`, `{{P_MFD}}`, `{{COT_CHOT}}` trong Word.

## 5. ƯỚC TÍNH SƠ BỘ
- **Độ phức tạp:** Cao (Cần thuật toán xử lý ngày tháng (date-fns hoặc python datetime) phức tạp để xử lý ngày 28/29/30/31).
- **Phạm vi áp dụng:** Chỉ áp dụng cho loại **Gia hạn** và **Thanh lý ký lại**.
- **Rủi ro:** Cần đảm bảo logic làm tròn không gây ra số âm ở mục "Mặt bằng".

## 6. BƯỚC TIẾP THEO
→ Chạy `/plan` để thiết kế chi tiết thuật toán tính ngày và cập nhật UI.

