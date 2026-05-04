import streamlit as st
import pandas as pd
import batch_processor as bp
from finance_service import FinanceService as fs
import os
from datetime import datetime

# Cấu hình trang
st.set_page_config(page_title="BTS Contract Automation", layout="wide")

st.title("🎨 BTS Contract Appendix Generator")
st.markdown("Hệ thống tự động soạn thảo phụ lục hợp đồng BTS (Mẫu 1245)")

# Load dữ liệu (cache để nhanh hơn)
@st.cache_data
def load_data():
    df_master = pd.read_excel(bp.MASTER_EXCEL)
    df_price = pd.read_excel(bp.PRICE_EXCEL, sheet_name='Chi tiết thuê trạm', header=None)
    return df_master, df_price

try:
    df_m, df_p = load_data()
    st.success("✅ Đã kết nối dữ liệu Master và Price Sheet.")
except Exception as e:
    st.error(f"❌ Lỗi tải dữ liệu: {e}")
    st.stop()

# Giao diện tìm kiếm
col1, col2 = st.columns([2, 1])
with col1:
    search_query = st.text_input("🔍 Tìm kiếm trạm (Nhập Site ID):", placeholder="VD: DNCM01")

if search_query:
    results = df_m[df_m.iloc[:, 2].astype(str).str.contains(search_query, na=False, case=False)]
    
    if results.empty:
        st.warning("⚠️ Không tìm thấy trạm nào khớp với mã trên.")
    else:
        st.write(f"Tìm thấy {len(results)} kết quả:")
        
        selected_site_idx = st.selectbox("Chọn trạm cần xử lý:", 
                                         options=results.index, 
                                         format_func=lambda x: f"{results.loc[x].iloc[2]} - {results.loc[x].iloc[10]}")
        
        row = results.loc[selected_site_idx]
        site_id = str(row.iloc[2]).strip()
        
        # Tính toán lịch trình
        with st.spinner("Đang tính toán lịch trình thanh toán..."):
            schedule = bp.get_site_schedule(row, df_p)
            
        if not schedule:
            st.error("❌ Không tìm thấy thông tin giá của trạm này trong Price Sheet.")
        else:
            # Hiển thị thông tin tổng quan
            st.subheader(f"📍 Thông tin trạm: {site_id}")
            c_info1, c_info2, c_info3 = st.columns(3)
            with c_info1:
                st.metric("Đơn giá cũ", fs.format_vn_currency(schedule["old_price"]))
            with c_info2:
                st.metric("Đơn giá mới", fs.format_vn_currency(schedule["new_price"]))
            with c_info3:
                st.metric("Khấu trừ Kỳ 1", fs.format_vn_currency(schedule["deduction"]))

            # Hiển thị bảng thanh toán preview
            st.subheader("📅 Bảng Thanh Toán Dự Kiến")
            
            period_data = []
            for p in schedule["periods"]:
                period_data.append({
                    "Kỳ": p["no"],
                    "Từ ngày": p["start"].strftime("%d/%m/%Y"),
                    "Đến ngày": p["end"].strftime("%d/%m/%Y"),
                    "Số tiền (VNĐ)": fs.format_vn_currency(p["amount"])
                })
            
            st.table(period_data)
            st.info(f"**Tổng cộng hợp đồng:** {fs.format_vn_currency(schedule['total_amount'])} VNĐ")

            # Nút xuất file
            if st.button("🚀 XUẤT FILE PHỤ LỤC (.WORD)"):
                with st.spinner("Đang tạo file Word..."):
                    ok, file_path = bp.process_site(row, df_p)
                    if ok:
                        st.success(f"✅ Đã tạo file thành công!")
                        with open(file_path, "rb") as f:
                            btn = st.download_button(
                                label="📥 TẢI FILE VỀ MÁY",
                                data=f,
                                file_name=os.path.basename(file_path),
                                mime="application/vnd.openxmlformats-officedocument.wordprocessingml.document"
                            )
                    else:
                        st.error(f"❌ Lỗi khi tạo file: {file_path}")

st.divider()
st.caption("Giao diện được phát triển bởi Antigravity Assistant - 2026")
