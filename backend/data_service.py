import pandas as pd
import os
import math

class DataService:
    def __init__(self, data_dir="data_source"):
        self.data_dir = data_dir
        self.files = {
            "contracts": "DANH_SACH_HOP_DONG_MAT_BANG_NHA_TRAM_21_04_2026.xlsx",
            "prices_old": "DS1245 PLHD.xlsx",
            "prices_new": "MBF ĐNa_BC_VB 1245_BÁO CÁO NGÀY.xlsx",
            "addresses": "TOAN BO DU LIEU_1278_TRAM_cang.letan_20260421_091229.xlsx"
        }

    def _scan_for_site(self, file_path, site_id, sheet_name=0):
        """Quét toàn bộ file để tìm dòng chứa Site ID"""
        try:
            df = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
            for i, row in df.iterrows():
                row_vals = [str(x).strip().upper() for x in row.values]
                if site_id.upper() in row_vals:
                    # Giả định dòng tiêu đề nằm ở vài dòng phía trên dòng chứa Site ID
                    # Nhưng để chắc chắn, ta trả về cả dataframe và vị trí dòng dữ liệu
                    return df, i
            return None, None
        except Exception as e:
            return None, None

    def get_full_site_info(self, site_id):
        """Thu thập dữ liệu thô từ cả 4 nguồn"""
        res = {
            "contracts": None,
            "prices_daily": None, 
            "prices_1245": None,
            "address": None
        }

        # 1. Quét file Hợp đồng
        df, idx = self._scan_for_site(os.path.join(self.data_dir, self.files["contracts"]), site_id)
        if df is not None:
            res["contracts"] = df.iloc[idx].to_dict()

        # 2. Quét file Báo cáo ngày (Sheet: Chi tiết thuê trạm)
        df, idx = self._scan_for_site(os.path.join(self.data_dir, self.files["prices_new"]), site_id, sheet_name="Chi tiết thuê trạm")
        if df is not None:
            res["prices_daily"] = df.iloc[idx].to_dict()

        # 3. Quét file 1245 cũ
        df, idx = self._scan_for_site(os.path.join(self.data_dir, self.files["prices_old"]), site_id)
        if df is not None:
            res["prices_1245"] = df.iloc[idx].to_dict()

        # 4. Quét file Địa chỉ
        df, idx = self._scan_for_site(os.path.join(self.data_dir, self.files["addresses"]), site_id)
        if df is not None:
            res["address"] = df.iloc[idx].to_dict()

        return res

    @staticmethod
    def round_down_50k(amount):
        """Làm tròn xuống mức 50.000đ gần nhất"""
        if pd.isna(amount) or not isinstance(amount, (int, float)):
            return amount
        return math.floor(amount / 50000) * 50000
