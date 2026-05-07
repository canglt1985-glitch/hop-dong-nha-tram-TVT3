import os
import sys
import json
import math
import requests
import io
import threading
import pandas as pd
from datetime import datetime
from dateutil.relativedelta import relativedelta
from fastapi import FastAPI, HTTPException, Body
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel
from typing import Dict, Optional, List

# Add the parent directory to Python path to import generate_thanh_ly_contract if needed
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

app = FastAPI(title="BTS Contract Automation API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuration Paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
WORKSPACE_DIR = os.path.dirname(BASE_DIR)
EXCEL_PATH = r"D:\Chuyen doi so\soan HD\DATA HOP DONG.xlsx"
PROGRESS_FILE = os.path.join(BASE_DIR, "progress_tracker.json")
CONFIG_FILE = os.path.join(BASE_DIR, "config.json")
OUTPUT_DIR = os.path.join(WORKSPACE_DIR, "output")

if not os.path.exists(OUTPUT_DIR):
    os.makedirs(OUTPUT_DIR)

# --- CONFIG UTILITIES ---
def load_config() -> Dict:
    default_config = {
        "spreadsheet_id": "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g",
        "web_app_url": ""
    }
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return {**default_config, **json.load(f)}
        except Exception:
            return default_config
    return default_config

def save_config(config_data: Dict):
    try:
        with open(CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(config_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving config: {e}")

# --- PROGRESS UTILITIES ---
def load_progress() -> Dict:
    if os.path.exists(PROGRESS_FILE):
        try:
            with open(PROGRESS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_progress(progress_data: Dict):
    try:
        with open(PROGRESS_FILE, "w", encoding="utf-8") as f:
            json.dump(progress_data, f, ensure_ascii=False, indent=2)
    except Exception as e:
        print(f"Error saving progress: {e}")

def parse_numeric_value(val) -> float:
    if pd.isna(val):
        return 0.0
    if isinstance(val, (int, float)):
        return float(val)
    val_str = str(val).strip()
    if not val_str:
        return 0.0
    try:
        # Remove common currency symbols, spaces
        val_str = val_str.replace("đ", "").replace("VND", "").replace(" ", "").replace("\xa0", "").strip()
        # Handle Vietnamese formatting where '.' is thousands and ',' is decimal
        if "." in val_str and "," in val_str:
            val_str = val_str.replace(".", "").replace(",", ".")
        elif "." in val_str:
            parts = val_str.split(".")
            if len(parts) > 2 or (len(parts) == 2 and len(parts[1]) == 3):
                val_str = val_str.replace(".", "")
            else:
                pass
        elif "," in val_str:
            val_str = val_str.replace(",", ".")
        return float(val_str)
    except Exception:
        return 0.0


# --- ONLINE SYNC MECHANISM ---
def fetch_online_progress(web_app_url: str) -> Optional[Dict]:
    """Fetches the latest progress data from the Google Sheets via Apps Script Web App."""
    if not web_app_url or not web_app_url.strip():
        return None
    try:
        response = requests.get(web_app_url, timeout=5)
        if response.status_code == 200:
            online_rows = response.json()
            # Convert list of rows back to site_id dictionary
            online_dict = {}
            for row in online_rows:
                site_id = row.get("site_id")
                if site_id:
                    online_dict[site_id] = {
                        "selected_template": row.get("selected_template", "thanh_ly_ky_lai"),
                        "status": row.get("status", "dong_y"),
                        "new_contract_no": row.get("new_contract_no", ""),
                        "new_contract_date": row.get("new_contract_date", ""),
                        "new_price_confirmed": float(row["new_price_confirmed"]) if row.get("new_price_confirmed") else None,
                        "progress": {
                            "draft_prepared": row.get("draft_prepared") == "TRUE",
                            "submitted_internal": row.get("submitted_internal") == "TRUE",
                            "signed_and_stamped": row.get("signed_and_stamped") == "TRUE",
                            "archived_doc": row.get("archived_doc") == "TRUE"
                        },
                        "last_updated": row.get("last_updated", datetime.now().isoformat())
                    }
            return online_dict
    except Exception as e:
        print(f"Warning: Failed to fetch online progress from Web App: {e}")
    return None

def sync_post_to_google_sheet_async(web_app_url: str, payload: Dict):
    """Sends progress update to Google Sheets Web App in a background thread."""
    def run():
        if not web_app_url or not web_app_url.strip():
            return
        try:
            headers = {"Content-Type": "application/json"}
            requests.post(web_app_url, data=json.dumps(payload), headers=headers, timeout=10)
            print("Successfully synced progress record to Google Sheets online!")
        except Exception as e:
            print(f"Error syncing to Google Sheets: {e}")
    threading.Thread(target=run, daemon=True).start()

# --- PYDANTIC SCHEMAS ---
class ProgressUpdate(BaseModel):
    site_id: str
    selected_template: str
    status: str
    progress: Dict[str, bool]
    new_contract_no: Optional[str] = None
    new_contract_date: Optional[str] = None
    new_price_confirmed: Optional[float] = None

class SettingsUpdate(BaseModel):
    spreadsheet_id: str
    web_app_url: str

# --- DYNAMIC COLUMN INDEX FINDER ---
def find_header_indices(df: pd.DataFrame) -> Dict[str, int]:
    """
    Scans Row index 6 (Row 7 in spreadsheet) for exact and fuzzy matching header terms
    to prevent index shifting issues between Google Sheets and local Excel.
    """
    headers = [str(x).strip().lower() if pd.notna(x) else "" for x in df.iloc[6]]
    
    # Defaults based on standard Excel layout
    mapping = {
        "site_id": 1,          # 'Mã trạm'
        "owner": 16,           # 'Chủ thể hợp đồng'
        "end_date": 26,        # 'Ngày kết thúc HĐ'
        "payment_cycle": 70,   # 'Chu kỳ thanh toán'
        "account_owner": 87,   # 'Chủ tài khoản'
        "account_no": 88,      # 'Số tài khoản'
        "bank_name": 89,       # 'Ngân hàng'
        "bank_branch": 90,     # 'Chi nhánh'
        "to_vt": 91,           # 'Tổ'
        "dat_muc_tieu_1245": 11, # 'Đạt mục tiêu 1245 (trước đàm phán)'
        "duoc_thanh_toan_1245": 12 # 'Được thanh toán theo 1245'
    }
    
    # Try to scan and update mapping dynamically
    for idx, h in enumerate(headers):
        if "mã trạm" in h or h == "id trạm":
            mapping["site_id"] = idx
        elif "chủ thể hợp đồng" in h or "bên cho thuê" in h or h == "chủ nhà":
            mapping["owner"] = idx
        elif "ngày kết thúc hđ" in h or h == "hạn hợp đồng":
            mapping["end_date"] = idx
        elif "chu kỳ thanh toán" in h or h == "chu kỳ":
            mapping["payment_cycle"] = idx
        elif "đạt mục tiêu 1245" in h:
            mapping["dat_muc_tieu_1245"] = idx
        elif "được thanh toán theo 1245" in h:
            mapping["duoc_thanh_toan_1245"] = idx
        elif "chủ tài khoản" in h:
            mapping["account_owner"] = idx
            # Bank details are strictly sequential following account_owner
            mapping["account_no"] = idx + 1
            mapping["bank_name"] = idx + 2
            mapping["bank_branch"] = idx + 3
            mapping["to_vt"] = idx + 4

    return mapping

# --- API ENDPOINTS ---

@app.get("/")
def root():
    return {"message": "BTS Contract Automation API is online", "status": "online"}

@app.get("/settings")
def get_settings():
    return load_config()

@app.post("/settings")
def update_settings(data: SettingsUpdate):
    config = {
        "spreadsheet_id": data.spreadsheet_id.strip(),
        "web_app_url": data.web_app_url.strip()
    }
    save_config(config)
    return {"success": True, "settings": config}

@app.get("/sites")
def get_sites():
    """
    Loads sites from Google Sheets directly (online master data), 
    falling back to local DATA HOP DONG.xlsx if offline.
    """
    config = load_config()
    spreadsheet_id = config.get("spreadsheet_id", "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g")
    web_app_url = config.get("web_app_url", "")
    
    df = None
    loaded_online = False
    
    # 1. Attempt to load master data online from Google Sheets (Public CSV Export)
    if spreadsheet_id:
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=hopdong"
        try:
            print(f"Fetching master contract data from Google Sheet: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                df = pd.read_csv(io.StringIO(response.text), header=None)
                loaded_online = True
                print(f"Successfully loaded {df.shape[0]} rows online from Google Sheets!")
        except Exception as e:
            print(f"Warning: Failed to load from Google Sheets ({e}). Falling back to local Excel.")

    # 2. Fall back to local Excel if Google Sheets fetch fails
    if df is None:
        if not os.path.exists(EXCEL_PATH):
            raise HTTPException(status_code=404, detail="Master data source not found (Google Sheets offline and local Excel missing).")
        try:
            print("Loading master contract data from local Excel file...")
            df = pd.read_excel(EXCEL_PATH, sheet_name="FULL-(XHH-LK)", header=None)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error reading local Excel fallback: {str(e)}")

    # 1b. Fetch VB1245 sheet online if available
    vb_map = {}
    if spreadsheet_id:
        url_vb = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/gviz/tq?tqx=out:csv&sheet=VB1245"
        try:
            print(f"Fetching VB1245 data from Google Sheet: {url_vb}")
            response_vb = requests.get(url_vb, timeout=5)
            if response_vb.status_code == 200:
                df_vb = pd.read_csv(io.StringIO(response_vb.text), header=None)
                # Starts from row 7 (index 7)
                for r in range(7, df_vb.shape[0]):
                    v_id_val = df_vb.iloc[r, 1]
                    v_id = str(v_id_val).strip() if pd.notna(v_id_val) else ""
                    if v_id and v_id != "nan" and v_id != "None":
                        val_5 = str(df_vb.iloc[r, 5]).strip() if pd.notna(df_vb.iloc[r, 5]) else ""
                        val_9 = str(df_vb.iloc[r, 9]).strip() if pd.notna(df_vb.iloc[r, 9]) else ""
                        val_16 = str(df_vb.iloc[r, 16]).strip() if pd.notna(df_vb.iloc[r, 16]) else ""
                        val_89 = str(df_vb.iloc[r, 89]).strip() if pd.notna(df_vb.iloc[r, 89]) else ""
                        val_90 = str(df_vb.iloc[r, 90]).strip() if pd.notna(df_vb.iloc[r, 90]) else ""
                        val_91 = str(df_vb.iloc[r, 91]).strip() if pd.notna(df_vb.iloc[r, 91]) else ""
                        val_95 = str(df_vb.iloc[r, 95]).strip() if pd.notna(df_vb.iloc[r, 95]) else ""
                        val_96 = str(df_vb.iloc[r, 96]).strip() if pd.notna(df_vb.iloc[r, 96]) else ""
                        
                        ht_price = parse_numeric_value(val_5)
                        mt_price = parse_numeric_value(val_9)
                        reduction_amount = parse_numeric_value(val_91)
                        reduced_price = parse_numeric_value(val_95)
                        
                        # Has agreed is True if cols 89, 90, 91 are filled and valid
                        has_agreed = False
                        if val_89 and val_90 and val_91 and val_89 != "-" and val_90 != "-" and val_91 != "-":
                            has_agreed = True
                        
                        vb_map[v_id] = {
                            "has_agreed_1245": has_agreed,
                            "ht_price": ht_price,
                            "mt_price": mt_price,
                            "negotiation_date": val_89,
                            "effective_date": val_90,
                            "reduction_amount": reduction_amount,
                            "reduced_price": reduced_price,
                            "reached_target": val_96
                        }
                print(f"Successfully loaded and parsed {len(vb_map)} VB1245 site mappings!")
        except Exception as e:
            print(f"Warning: Failed to fetch/parse VB1245 sheet ({e}).")

    try:
        # Load local progress data
        progress_data = load_progress()
        
        # 3. Synchronize with Online progress spreadsheet if Web App is configured
        if web_app_url:
            online_progress = fetch_online_progress(web_app_url)
            if online_progress:
                # Merge online progress (newer data wins or takes precedence)
                for site_id, online_rec in online_progress.items():
                    progress_data[site_id] = online_rec
                save_progress(progress_data)

        # Get dynamic column mapping indices
        col_map = find_header_indices(df)
        print("Resolved Column Mapping Indices:", col_map)
        
        sites_list = []
        for r_idx in range(7, df.shape[0]):  # Starts from row index 7 for actual data rows
            site_id_val = df.iloc[r_idx, col_map["site_id"]]
            site_id = str(site_id_val).strip() if pd.notna(site_id_val) else ""
            if not site_id or site_id == "nan" or site_id == "None":
                continue
                
            owner_name = str(df.iloc[r_idx, col_map["owner"]]).strip() if pd.notna(df.iloc[r_idx, col_map["owner"]]) else "Chưa rõ"
            end_date_val = df.iloc[r_idx, col_map["end_date"]]
            
            # Format expiry date
            end_date_str = ""
            needs_ext = False
            if pd.notna(end_date_val):
                if isinstance(end_date_val, datetime):
                    end_date_str = end_date_val.strftime("%d/%m/%Y")
                    needs_ext = end_date_val < datetime(2027, 7, 1)
                else:
                    end_date_str = str(end_date_val).strip()
                    # Try to parse string dates
                    try:
                        parsed_dt = datetime.strptime(end_date_str, "%d/%m/%Y")
                        needs_ext = parsed_dt < datetime(2027, 7, 1)
                    except ValueError:
                        try:
                            parsed_dt = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
                            end_date_str = parsed_dt.strftime("%d/%m/%Y")
                            needs_ext = parsed_dt < datetime(2027, 7, 1)
                        except ValueError:
                            # Fuzzy fallbacks
                            needs_ext = "2026" in end_date_str or "2025" in end_date_str or "2024" in end_date_str
            else:
                end_date_str = "Chưa rõ"
                needs_ext = True
                    
            ext_status = "🔴 Cần gia hạn" if needs_ext else "🟢 Còn hạn"
            
            # Robust extraction of old_price
            old_price = parse_numeric_value(df.iloc[r_idx, 43])
            if old_price == 0:
                old_price = parse_numeric_value(df.iloc[r_idx, 44])
            if old_price == 0:
                old_price = parse_numeric_value(df.iloc[r_idx, 42])
                
            # Apply column index offset of +1 if loaded online from Google Sheets (due to a blank col at index 42)
            offset = 1 if loaded_online else 0
            
            # --- HARMONIZED PRICING EXTRACTION (Indices 47 to 67) ---
            mb_raw = parse_numeric_value(df.iloc[r_idx, 47 + offset])
            
            # Room/Shelter types dynamic scanning (Indices 48 to 54)
            pm_raw = 0.0
            pm_label_val = "Phòng máy mặt đất"
            for col_i in range(48, 55):
                val = parse_numeric_value(df.iloc[r_idx, col_i + offset])
                if val > 0:
                    pm_raw = val
                    try:
                        title = str(df.iloc[6, col_i + offset]).strip()
                        if title and title.lower() != 'nan':
                            pm_label_val = title.capitalize()
                    except Exception:
                        pass
                    break
                    
            # Generator Room (Index 55)
            mfd_raw = parse_numeric_value(df.iloc[r_idx, 55 + offset])
            
            # Tower types dynamic scanning (Indices 56 to 58)
            cot_raw = 0.0
            for col_i in range(56, 59):
                val = parse_numeric_value(df.iloc[r_idx, col_i + offset])
                if val > 0:
                    cot_raw = val
                    break
                    
            # Shared Tower Discount (Index 67)
            giam_tru_raw = parse_numeric_value(df.iloc[r_idx, 67 + offset])
            
            # Google Sheets might export small numbers representing thousands (e.g., 300.0 instead of 300000)
            if loaded_online:
                if 0 < abs(mb_raw) < 10000: mb_raw *= 1000
                if 0 < abs(pm_raw) < 10000: pm_raw *= 1000
                if 0 < abs(mfd_raw) < 10000: mfd_raw *= 1000
                if 0 < abs(cot_raw) < 10000: cot_raw *= 1000
                if 0 < abs(giam_tru_raw) < 10000: giam_tru_raw *= 1000
                
            # Auxiliary Extra Items scanning (Indices 59 to 66)
            other_items = []
            other_items_raw_total = 0.0
            other_items_pay_total = 0.0
            for col_i in range(59, 67):
                val = parse_numeric_value(df.iloc[r_idx, col_i + offset])
                if val > 0:
                    if loaded_online and 0 < abs(val) < 10000:
                        val *= 1000
                    raw_val = val
                    pay_val = (int(raw_val) // 50000) * 50000
                    try:
                        title = str(df.iloc[6, col_i + offset]).strip()
                    except Exception:
                        title = ""
                    if not title or title.lower() == 'nan':
                        title = f"Hạng mục Index {col_i}"
                    other_items.append({
                        "title": title.capitalize(),
                        "raw": raw_val,
                        "pay": pay_val
                    })
                    other_items_raw_total += raw_val
                    other_items_pay_total += pay_val
                    
            # --- 3-LAYER ROUNDING MATHS (Unified with VB1245) ---
            # Layer 1: Round Antenna Tower price including negative sharing discounts
            cot_price_pay = ((int(cot_raw) + int(giam_tru_raw)) // 50000) * 50000
            
            # Layer 2: Temporary sum rounded down to nearest 50,000 for standard compliance
            temp_total = mb_raw + pm_raw + mfd_raw + cot_price_pay + other_items_raw_total
            new_price_val = (int(temp_total) // 50000) * 50000
            
            # Layer 3: Round room/generator prices and plug the remaining portion into Mặt bằng
            pm_price_pay = (int(pm_raw) // 50000) * 50000 if pm_raw > 0 else 0
            mfd_price_pay = (int(mfd_raw) // 50000) * 50000 if mfd_raw > 0 else 0
            mb_price_pay = new_price_val - pm_price_pay - mfd_price_pay - cot_price_pay - other_items_pay_total
            
            mb_price = mb_price_pay
            pm_price = pm_price_pay
            mfd_price = mfd_price_pay
            cot_price = cot_raw
            giam_tru = giam_tru_raw
            
            # Retrieve VB1245 specific details
            vb_info = vb_map.get(site_id, {})
            has_agreed_vb = vb_info.get("has_agreed_1245", False)
            ht_price_vb = vb_info.get("ht_price", 0)
            mt_price_vb = vb_info.get("mt_price", 0)
            reduction_amount_vb = vb_info.get("reduction_amount", 0)
            reduced_price_vb = vb_info.get("reduced_price", 0)
            reached_target_vb = vb_info.get("reached_target", "")
            negotiation_date_vb = vb_info.get("negotiation_date", "")
            effective_date_vb = vb_info.get("effective_date", "")
            
            # Determine if price addendum is even needed (HT <= MT)
            no_addendum_needed = False
            if ht_price_vb > 0 and mt_price_vb > 0 and ht_price_vb <= mt_price_vb:
                no_addendum_needed = True

            # Smart determination of new_price
            if site_id in progress_data and progress_data[site_id].get("new_price_confirmed"):
                new_price = int(progress_data[site_id]["new_price_confirmed"])
            elif has_agreed_vb and reduced_price_vb > 0:
                new_price = int(reduced_price_vb)
            elif has_agreed_vb and reduction_amount_vb > 0:
                new_price = int(old_price - reduction_amount_vb)
            else:
                # Fallback to calculated new price from elements
                elem_price = int(new_price_val)
                new_price = elem_price if elem_price > 0 else int(old_price)
            
            # Extracted details for payment cycles and bank compliance
            payment_cycle = str(df.iloc[r_idx, col_map["payment_cycle"]]).strip() if pd.notna(df.iloc[r_idx, col_map["payment_cycle"]]) else "6 tháng"
            account_owner = str(df.iloc[r_idx, col_map["account_owner"]]).strip() if pd.notna(df.iloc[r_idx, col_map["account_owner"]]) else owner_name
            account_no = str(df.iloc[r_idx, col_map["account_no"]]).strip() if pd.notna(df.iloc[r_idx, col_map["account_no"]]) else ""
            bank_name = str(df.iloc[r_idx, col_map["bank_name"]]).strip() if pd.notna(df.iloc[r_idx, col_map["bank_name"]]) else ""
            bank_branch = str(df.iloc[r_idx, col_map["bank_branch"]]).strip() if pd.notna(df.iloc[r_idx, col_map["bank_branch"]]) else ""
            to_vt = str(df.iloc[r_idx, col_map["to_vt"]]).strip() if pd.notna(df.iloc[r_idx, col_map["to_vt"]]) else "Chưa rõ"
            dat_muc_tieu_1245 = str(df.iloc[r_idx, col_map["dat_muc_tieu_1245"]]).strip() if pd.notna(df.iloc[r_idx, col_map["dat_muc_tieu_1245"]]) else ""
            duoc_thanh_toan_1245 = str(df.iloc[r_idx, col_map["duoc_thanh_toan_1245"]]).strip() if pd.notna(df.iloc[r_idx, col_map["duoc_thanh_toan_1245"]]) else ""

            # Match checking: check if the bank account name matches the landlord name
            is_owner_match = owner_name.lower().strip() in account_owner.lower().strip() or account_owner.lower().strip() in owner_name.lower().strip()
            owner_match_status = "✅ Khớp" if is_owner_match else f"⚠️ Lệch (Bank: {account_owner})"
            
            # Determine dynamic default status based on VB1245 agreement or expiry
            if has_agreed_vb:
                default_status = "dong_y"
            elif needs_ext:
                default_status = "can_thanh_ly"
            else:
                default_status = "dong_y"  # If not agreed and not expired, it defaults to active contract (reducing price workflow)

            # Fetch progress if any
            prog_info = progress_data.get(site_id, {
                "selected_template": "thanh_ly_ky_lai" if needs_ext else "phu_luc_giam_gia",
                "status": default_status,
                "new_contract_no": "",
                "new_contract_date": "",
                "new_price_confirmed": None,
                "progress": {
                    "draft_prepared": False,
                    "submitted_internal": False,
                    "signed_and_stamped": False,
                    "archived_doc": False
                }
            })
            if "status" not in prog_info:
                prog_info["status"] = default_status
            if "new_contract_no" not in prog_info:
                prog_info["new_contract_no"] = ""
            if "new_contract_date" not in prog_info:
                prog_info["new_contract_date"] = ""
            if "new_price_confirmed" not in prog_info:
                prog_info["new_price_confirmed"] = None
            
            sites_list.append({
                "site_id": site_id,
                "owner": owner_name,
                "end_date": end_date_str,
                "ext_status": ext_status,
                "old_price": old_price,
                "new_price": new_price,
                "dat_muc_tieu_1245": dat_muc_tieu_1245,
                "duoc_thanh_toan_1245": duoc_thanh_toan_1245,
                "has_agreed_1245": has_agreed_vb,
                "no_addendum_needed": no_addendum_needed,
                "reached_target": reached_target_vb,
                "reduction_amount": reduction_amount_vb,
                "reduced_price": reduced_price_vb,
                "negotiation_date": negotiation_date_vb,
                "effective_date": effective_date_vb,
                "prices_breakdown": {
                    "mb": mb_price,
                    "pm": pm_price,
                    "mfd": mfd_price,
                    "cot": cot_price,
                    "giam_tru": giam_tru,
                    "cot_rounded": cot_price_pay
                },
                "payment_cycle": payment_cycle,
                "to_vt": to_vt,  # Organization/Operations Group VT1/2/3/4/5
                "banking_info": {
                    "account_owner": account_owner,
                    "account_no": account_no,
                    "bank_name": bank_name,
                    "bank_branch": bank_branch,
                    "is_owner_match": is_owner_match,
                    "match_status_text": owner_match_status
                },
                "progress_tracker": prog_info
            })
            
        return sites_list
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error compiling contract lists: {str(e)}")

@app.post("/progress")
def update_progress(data: ProgressUpdate):
    """Saves user progress update to local tracker file and triggers background sync to Google Sheets."""
    progress_data = load_progress()
    record = {
        "selected_template": data.selected_template,
        "status": data.status,
        "progress": data.progress,
        "new_contract_no": data.new_contract_no or "",
        "new_contract_date": data.new_contract_date or "",
        "new_price_confirmed": data.new_price_confirmed,
        "last_updated": datetime.now().isoformat()
    }
    progress_data[data.site_id] = record
    save_progress(progress_data)
    
    # Dispatch sync to Google Sheets online in background
    config = load_config()
    web_app_url = config.get("web_app_url", "")
    if web_app_url:
        sync_post_to_google_sheet_async(web_app_url, {data.site_id: record})
        
    return {"success": True, "data": progress_data[data.site_id], "synced_online": bool(web_app_url)}

@app.post("/generate/{site_id}")
def generate_document(site_id: str, template_type: str = Body(..., embed=True)):
    """Triggers dynamic docx generation for a specific site & template type."""
    site_id = site_id.upper()
    print(f"Generating docx for: {site_id} with template {template_type}")
    
    if template_type == "thanh_ly_ky_lai":
        from generate_thanh_ly_contract import generate_thanh_ly_contract
        try:
            success = generate_thanh_ly_contract(site_id)
            if success:
                # Update progress tracker to check draft_prepared = True
                progress_data = load_progress()
                if site_id not in progress_data:
                    progress_data[site_id] = {
                        "selected_template": template_type,
                        "status": "dong_y",
                        "new_contract_no": "",
                        "new_contract_date": "",
                        "new_price_confirmed": None,
                        "progress": {
                            "draft_prepared": True,
                            "submitted_internal": False,
                            "signed_and_stamped": False,
                            "archived_doc": False
                        }
                    }
                else:
                    progress_data[site_id]["progress"]["draft_prepared"] = True
                    progress_data[site_id]["selected_template"] = template_type
                
                progress_data[site_id]["last_updated"] = datetime.now().isoformat()
                save_progress(progress_data)
                
                # Dynamic background sync to Google Sheet
                config = load_config()
                web_app_url = config.get("web_app_url", "")
                if web_app_url:
                    sync_post_to_google_sheet_async(web_app_url, {site_id: progress_data[site_id]})
                
                output_path = os.path.join(OUTPUT_DIR, f"Thanh_Ly_Ky_Lai_{site_id}.docx")
                if os.path.exists(output_path):
                    return {"success": True, "filename": f"Thanh_Ly_Ky_Lai_{site_id}.docx", "progress": progress_data[site_id]}
                else:
                    raise HTTPException(status_code=500, detail="Output file was not found on disk after successful generation.")
            else:
                raise HTTPException(status_code=500, detail="Document generation process returned False.")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    elif template_type in ["phu_luc_giam_gia", "phu_luc_gia_han"]:
        import batch_processor as bp
        import pandas as pd
        import shutil
        
        try:
            print("Loading master lists for Phụ lục generation...")
            df_master = pd.read_excel(bp.MASTER_EXCEL)
            df_price = pd.read_excel(bp.PRICE_EXCEL, sheet_name='Chi tiết thuê trạm', header=None)
            
            # Find the row index matching site_id (which is in column index 2 of master Excel)
            row_idx = None
            for r in range(df_master.shape[0]):
                cell_val = df_master.iloc[r, 2]
                if pd.notna(cell_val) and str(cell_val).strip().upper() == site_id:
                    row_idx = r
                    break
                    
            if row_idx is None:
                raise HTTPException(status_code=404, detail=f"Không tìm thấy trạm {site_id} trong danh sách Master để soạn Phụ lục.")
                
            row = df_master.iloc[row_idx]
            
            # Create batch output folder if not exists
            if not os.path.exists(bp.O_DIR):
                os.makedirs(bp.O_DIR)
                
            success, out_file = bp.process_site(row, df_price)
            if success and out_file and os.path.exists(out_file):
                # Update progress tracker
                progress_data = load_progress()
                if site_id not in progress_data:
                    progress_data[site_id] = {
                        "selected_template": template_type,
                        "status": "dong_y",
                        "new_contract_no": "",
                        "new_contract_date": "",
                        "new_price_confirmed": None,
                        "progress": {
                            "draft_prepared": True,
                            "submitted_internal": False,
                            "signed_and_stamped": False,
                            "archived_doc": False
                        }
                    }
                else:
                    progress_data[site_id]["progress"]["draft_prepared"] = True
                    progress_data[site_id]["selected_template"] = template_type
                
                progress_data[site_id]["last_updated"] = datetime.now().isoformat()
                save_progress(progress_data)
                
                # Dynamic background sync to Google Sheet
                config = load_config()
                web_app_url = config.get("web_app_url", "")
                if web_app_url:
                    sync_post_to_google_sheet_async(web_app_url, {site_id: progress_data[site_id]})
                
                # Determine destination file name based on type
                dest_filename = f"Phu_Luc_Giam_Gia_{site_id}.docx" if template_type == "phu_luc_giam_gia" else f"Phu_Luc_Gia_Han_{site_id}.docx"
                dest_path = os.path.join(OUTPUT_DIR, dest_filename)
                shutil.copy(out_file, dest_path)
                
                return {"success": True, "filename": dest_filename, "progress": progress_data[site_id]}
            else:
                raise HTTPException(status_code=500, detail=f"Lỗi khởi tạo tài liệu từ động cơ batch: {out_file}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
            
    else:
        raise HTTPException(status_code=501, detail=f"Template workflow '{template_type}' is registered but not yet implemented.")

@app.get("/download/{filename}")
def download_file(filename: str):
    """Serves compiled docx documents for downloading."""
    file_path = os.path.join(OUTPUT_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, filename=filename, media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document")
    raise HTTPException(status_code=404, detail="Requested file does not exist.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
