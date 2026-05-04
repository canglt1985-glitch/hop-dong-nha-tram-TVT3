from datetime import datetime, date
from dateutil.relativedelta import relativedelta
import math
import pandas as pd

class FinanceService:
    @staticmethod
    def calculate_extension(end_date_str):
        """Tính toán ngày hết hạn mới nếu trước 01/07/2026"""
        try:
            if isinstance(end_date_str, datetime):
                end_date = end_date_str
            else:
                # Thử các định dạng ngày phổ biến
                for fmt in ("%d/%m/%Y", "%Y-%m-%d %H:%M:%S", "%d/%m/%y"):
                    try:
                        end_date = datetime.strptime(str(end_date_str), fmt)
                        break
                    except: continue
                else: return end_date_str, False

            deadline = datetime(2026, 7, 1)
            if end_date < deadline:
                new_end_date = end_date + relativedelta(years=5)
                return new_end_date, True
            return end_date, False
        except Exception:
            return end_date_str, False

    @staticmethod
    def calculate_deduction(old_price, new_price, paid_until_str):
        """
        Tính toán số tiền khấu trừ từ mốc 01/10/2025
        paid_until: Ngày mà trạm đã thanh toán hết (trong quá khứ hoặc tương lai)
        """
        effective_date = datetime(2025, 10, 1)
        
        try:
            # Parse ngày đã thanh toán
            if isinstance(paid_until_str, datetime):
                paid_until = paid_until_str
            else:
                paid_until = pd.to_datetime(paid_until_str)
            
            if paid_until <= effective_date:
                return 0, 0 # Không cần khấu trừ vì chưa trả lố mốc 01/10

            # Tính số tháng trả lố (từ 01/10/2025 đến paid_until)
            diff = relativedelta(paid_until, effective_date)
            months_overpaid = diff.years * 12 + diff.months + (1 if diff.days > 15 else 0)
            
            # Chênh lệch mỗi tháng
            monthly_diff = old_price - new_price
            total_deduction = monthly_diff * months_overpaid
            
            return total_deduction, months_overpaid
        except Exception as e:
            print(f"Lỗi tính khấu trừ: {e}")
            return 0, 0

    @staticmethod
    def format_vn_currency(amount):
        """Định dạng tiền VNĐ"""
        if pd.isna(amount): return "0"
        return "{:,.0f}".format(amount).replace(",", ".")

    @staticmethod
    def format_to_text(amount):
        """Đọc số thành chữ tiếng Việt"""
        from num2words import num2words
        if pd.isna(amount) or amount == 0: return "Không đồng"
        text = num2words(amount, lang='vi').capitalize()
        return f"{text} đồng"
