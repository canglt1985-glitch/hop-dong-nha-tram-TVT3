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

from utils.data_utils import parse_numeric_value, find_header_indices
from services.sync_service import fetch_online_progress, sync_post_to_google_sheet_async
from utils.pricing_utils import calculate_pricing_breakdown
from word_service import WordService

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

import time

# --- CACHE ---
SITE_CACHE = {
    "data": None,
    "last_fetched": 0
}
CACHE_TTL = 1800  # 30 minutes

@app.get("/sites")
def get_sites(force_refresh: bool = False):
    """
    Loads sites from Google Sheets directly (online master data), 
    falling back to local DATA HOP DONG.xlsx if offline.
    """
    global SITE_CACHE
    
    if not force_refresh and SITE_CACHE["data"] is not None:
        if time.time() - SITE_CACHE["last_fetched"] < CACHE_TTL:
            print("Returning sites from cache...")
            return SITE_CACHE["data"]

    config = load_config()
    spreadsheet_id = config.get("spreadsheet_id", "19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g")
    web_app_url = config.get("web_app_url", "")
    
    df = None
    loaded_online = False
    
    # 1. Attempt to load master data online from Google Sheets (Public CSV Export)
    if spreadsheet_id:
        url = f"https://docs.google.com/spreadsheets/d/{spreadsheet_id}/export?format=csv&gid=0"
        try:
            print(f"Fetching master contract data from Google Sheet: {url}")
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                response.encoding = 'utf-8'
                df = pd.read_csv(io.StringIO(response.text), header=None, dtype=str)
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
            df = pd.read_excel(EXCEL_PATH, sheet_name="FULL-(XHH-LK)", header=None, dtype=str)
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
                response_vb.encoding = 'utf-8'
                df_vb = pd.read_csv(io.StringIO(response_vb.text), header=None, dtype=str)
                # Starts from row 7 (index 7)
                for r in range(7, df_vb.shape[0]):
                    v_id_val = df_vb.iloc[r, 1]
                    v_id = str(v_id_val).strip() if pd.notna(v_id_val) else ""
                    if v_id and v_id != "nan" and v_id != "None":
                        val_5 = str(df_vb.iloc[r, 5]).strip() if pd.notna(df_vb.iloc[r, 5]) else ""
                        val_9 = str(df_vb.iloc[r, 9]).strip() if pd.notna(df_vb.iloc[r, 9]) else ""
                        val_16 = str(df_vb.iloc[r, 16]).strip() if pd.notna(df_vb.iloc[r, 16]) else ""
                        val_80 = str(df_vb.iloc[r, 80]).strip() if pd.notna(df_vb.iloc[r, 80]) else ""
                        val_81 = str(df_vb.iloc[r, 81]).strip() if pd.notna(df_vb.iloc[r, 81]) else ""
                        val_82 = str(df_vb.iloc[r, 82]).strip() if pd.notna(df_vb.iloc[r, 82]) else ""
                        val_95 = str(df_vb.iloc[r, 95]).strip() if pd.notna(df_vb.iloc[r, 95]) else ""
                        val_96 = str(df_vb.iloc[r, 96]).strip() if pd.notna(df_vb.iloc[r, 96]) else ""
                        
                        ht_price = parse_numeric_value(val_5)
                        mt_price = parse_numeric_value(val_9)
                        reduction_amount = parse_numeric_value(val_81)
                        reduced_price = parse_numeric_value(val_95)
                        
                        # Has agreed is True if cols 80 (CC) is 'x' OR 81 (CD) has value OR 82 (CE) has value
                        has_agreed = False
                        if val_80.lower() == 'x' or (val_81 and val_81 not in ['-', 'nan']) or (val_82 and val_82 not in ['-', 'nan']):
                            has_agreed = True
                        
                        # Extract pricing breakdown from VB1245
                        mb_raw = parse_numeric_value(df_vb.iloc[r, 42])
                        pm_raw = max([parse_numeric_value(df_vb.iloc[r, c]) for c in range(43, 49)] + [0.0])
                        mfd_raw = parse_numeric_value(df_vb.iloc[r, 50])
                        cot_raw = max([parse_numeric_value(df_vb.iloc[r, c]) for c in range(51, 54)] + [0.0])
                        giam_tru_raw = parse_numeric_value(df_vb.iloc[r, 62])
                        vhkt_raw = parse_numeric_value(df_vb.iloc[r, 61])
                        
                        # Fix large values in thousands if necessary
                        if 0 < abs(mb_raw) < 10000: mb_raw *= 1000
                        if 0 < abs(pm_raw) < 10000: pm_raw *= 1000
                        if 0 < abs(mfd_raw) < 10000: mfd_raw *= 1000
                        if 0 < abs(cot_raw) < 10000: cot_raw *= 1000
                        if 0 < abs(giam_tru_raw) < 10000: giam_tru_raw *= 1000
                        if 0 < abs(vhkt_raw) < 10000: vhkt_raw *= 1000
                        
                        cot_rounded = round(cot_raw / 1000) * 1000
                        
                        vb_map[v_id] = {
                            "has_agreed_1245": has_agreed,
                            "ht_price": ht_price,
                            "mt_price": mt_price,
                            "negotiation_date": val_80,
                            "effective_date": val_81,
                            "reduction_amount": reduction_amount,
                            "reduced_price": reduced_price,
                            "reached_target": "", # Will be dynamically calculated later
                            "prices_breakdown": {
                                "mb": mb_raw,
                                "pm": pm_raw,
                                "mfd": mfd_raw,
                                "cot": cot_raw,
                                "giam_tru": giam_tru_raw,
                                "cot_rounded": cot_rounded,
                                "vhkt": vhkt_raw
                            }
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
            
            # Additional mapped fields
            contact_addr = str(df.iloc[r_idx, col_map.get("contact_addr", 17)]).strip() if "contact_addr" in col_map and pd.notna(df.iloc[r_idx, col_map["contact_addr"]]) else ""
            contract_no = str(df.iloc[r_idx, col_map.get("contract_no", 24)]).strip() if "contract_no" in col_map and pd.notna(df.iloc[r_idx, col_map["contract_no"]]) else ""
            phone = str(df.iloc[r_idx, col_map.get("phone", 12)]).strip() if "phone" in col_map and pd.notna(df.iloc[r_idx, col_map["phone"]]) else ""
            
            address_old = str(df.iloc[r_idx, col_map.get("address_old", 35)]).strip() if "address_old" in col_map and pd.notna(df.iloc[r_idx, col_map["address_old"]]) else ""
            address_new = str(df.iloc[r_idx, col_map.get("address_new", 41)]).strip() if "address_new" in col_map and pd.notna(df.iloc[r_idx, col_map["address_new"]]) else ""
            if address_new and address_new != "nan" and "Đồng Nai" not in address_new:
                address_new += ", Đồng Nai"
                
            hs_phap_ly = str(df.iloc[r_idx, col_map.get("hs_phap_ly", 42)]).strip() if "hs_phap_ly" in col_map and pd.notna(df.iloc[r_idx, col_map["hs_phap_ly"]]) else ""
            
            contract_date_val = df.iloc[r_idx, col_map["contract_date"]] if "contract_date" in col_map else None
            contract_date_str = ""
            if pd.notna(contract_date_val):
                if isinstance(contract_date_val, datetime):
                    contract_date_str = contract_date_val.strftime("%d/%m/%Y")
                else:
                    contract_date_str = str(contract_date_val).strip()
            
            end_date_val = df.iloc[r_idx, col_map["end_date"]]
            
            # Format expiry date
            end_date_str = ""
            needs_ext = False
            if pd.notna(end_date_val):
                if isinstance(end_date_val, datetime):
                    end_date_str = end_date_val.strftime("%d/%m/%Y")
                    needs_ext = end_date_val < datetime(2026, 7, 1)
                else:
                    end_date_str = str(end_date_val).strip()
                    # Try to parse string dates
                    try:
                        parsed_dt = datetime.strptime(end_date_str, "%d/%m/%Y")
                        needs_ext = parsed_dt < datetime(2026, 7, 1)
                    except ValueError:
                        try:
                            parsed_dt = datetime.strptime(end_date_str, "%Y-%m-%d %H:%M:%S")
                            end_date_str = parsed_dt.strftime("%d/%m/%Y")
                            needs_ext = parsed_dt < datetime(2026, 7, 1)
                        except ValueError:
                            # Fuzzy fallbacks
                            needs_ext = "2026" in end_date_str or "2025" in end_date_str or "2024" in end_date_str
            else:
                end_date_str = "Chưa rõ"
                needs_ext = True
                    
            ext_status = "🔴 Cần gia hạn" if needs_ext else "🟢 Còn hạn"
            
            site_type_val = str(df.iloc[r_idx, col_map.get("site_type", 8)]).strip() if "site_type" in col_map else ""
            site_type = site_type_val if site_type_val and site_type_val.lower() != "nan" else ""
            
            # Robust extraction of old_price
            old_price = parse_numeric_value(df.iloc[r_idx, 43])
            if old_price == 0:
                old_price = parse_numeric_value(df.iloc[r_idx, 44])
            if old_price == 0:
                old_price = parse_numeric_value(df.iloc[r_idx, 42])
                
            # Apply column index offset of +1 if loaded online from Google Sheets (due to a blank col at index 42)
            offset = 1 if loaded_online else 0
            
            # Retrieve VB1245 specific details first so we can use its pricing
            vb_info = vb_map.get(site_id, {})
            has_agreed_vb = vb_info.get("has_agreed_1245", False)
            ht_price_vb = vb_info.get("ht_price", 0)
            mt_price_vb = vb_info.get("mt_price", 0)
            reduction_amount_vb = vb_info.get("reduction_amount", 0)
            reduced_price_vb = vb_info.get("reduced_price", 0)
            reached_target_vb = vb_info.get("reached_target", "")
            negotiation_date_vb = vb_info.get("negotiation_date", "")
            effective_date_vb = vb_info.get("effective_date", "")
            prices_vb = vb_info.get("prices_breakdown", {})
            
            # Default fetch from hopdong sheet for fallback and other_items
            prices, new_price_val, other_items = calculate_pricing_breakdown(df, r_idx, offset, loaded_online)
            mb_price = prices['mb']
            pm_price = prices['pm']
            mfd_price = prices['mfd']
            cot_price = prices['cot']
            giam_tru = prices['giam_tru']
            cot_price_pay = prices['cot_rounded']
            vhkt_price = prices.get('vhkt', 0)
            
            # Since the user requested the price breakdown to be taken from VB1245 sheet, we override with prices_vb.
            if prices_vb:
                mb_price = prices_vb.get("mb", 0)
                pm_price = prices_vb.get("pm", 0)
                mfd_price = prices_vb.get("mfd", 0)
                cot_price = prices_vb.get("cot", 0)
                giam_tru = prices_vb.get("giam_tru", 0)
                cot_price_pay = prices_vb.get("cot_rounded", 0)
                vhkt_price = prices_vb.get("vhkt", 0)
                # Recompute new_price_val based on VB1245 values + other_items
                new_price_val = mb_price + pm_price + mfd_price + cot_price_pay + vhkt_price + sum(item['pay'] for item in other_items)

            
            # Determine if price addendum is even needed (HT <= MT)
            no_addendum_needed = False
            if ht_price_vb > 0 and mt_price_vb > 0 and ht_price_vb <= mt_price_vb:
                no_addendum_needed = True

            # Smart determination of new_price
            if site_id in progress_data and progress_data[site_id].get("new_price_confirmed"):
                new_price = int(progress_data[site_id]["new_price_confirmed"])
            elif reduced_price_vb > 0:
                new_price = int(reduced_price_vb)
            elif reduction_amount_vb > 0:
                new_price = int(old_price - reduction_amount_vb)
            else:
                # Fallback to calculated new price from elements
                elem_price = int(new_price_val)
                new_price = elem_price if elem_price > 0 else int(old_price)
                
            # Compute reached_target dynamically!
            if new_price > 0 and new_price_val > 0:
                if new_price <= new_price_val:
                    reached_target_vb = "Đạt"
                else:
                    reached_target_vb = "Không đạt"
            else:
                reached_target_vb = "Chưa đàm phán"

            
            # Extracted details for payment cycles and bank compliance
            payment_cycle = str(df.iloc[r_idx, col_map["payment_cycle"]]).strip() if pd.notna(df.iloc[r_idx, col_map["payment_cycle"]]) else "6 tháng"
            paid_until_date = str(df.iloc[r_idx, col_map["paid_until_date"]]).strip() if "paid_until_date" in col_map and pd.notna(df.iloc[r_idx, col_map["paid_until_date"]]) else ""
            account_owner = str(df.iloc[r_idx, col_map["account_owner"]]).strip() if pd.notna(df.iloc[r_idx, col_map["account_owner"]]) else owner_name
            account_no = str(df.iloc[r_idx, col_map["account_no"]]).strip() if pd.notna(df.iloc[r_idx, col_map["account_no"]]) else ""
            bank_name = str(df.iloc[r_idx, col_map["bank_name"]]).strip() if pd.notna(df.iloc[r_idx, col_map["bank_name"]]) else ""
            bank_branch = str(df.iloc[r_idx, col_map["bank_branch"]]).strip() if pd.notna(df.iloc[r_idx, col_map["bank_branch"]]) else ""
            to_vt = str(df.iloc[r_idx, col_map["to_vt"]]).strip() if pd.notna(df.iloc[r_idx, col_map["to_vt"]]) else "Chưa rõ"
            dat_muc_tieu_1245 = str(df.iloc[r_idx, col_map["dat_muc_tieu_1245"]]).strip() if pd.notna(df.iloc[r_idx, col_map["dat_muc_tieu_1245"]]) else ""
            duoc_thanh_toan_1245 = str(df.iloc[r_idx, col_map["duoc_thanh_toan_1245"]]).strip() if pd.notna(df.iloc[r_idx, col_map["duoc_thanh_toan_1245"]]) else ""
            hs_phap_ly = str(df.iloc[r_idx, col_map["hs_phap_ly"]]).strip() if "hs_phap_ly" in col_map and pd.notna(df.iloc[r_idx, col_map["hs_phap_ly"]]) else ""

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
            is_mbf = "MBF" in str(site_type).upper()
            default_ext_template = "phu_luc_gia_han" if is_mbf else "thanh_ly_ky_lai"
            
            prog_info = progress_data.get(site_id, {
                "selected_template": default_ext_template if needs_ext else "phu_luc_giam_gia",
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
                "contact_addr": contact_addr,
                "phone": phone,
                "contract_no": contract_no,
                "contract_date": contract_date_str,
                "address_old": address_old,
                "address_new": address_new,
                "hs_phap_ly": hs_phap_ly,
                "end_date": end_date_str,
                "paid_until_date": paid_until_date,
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
                    "cot_rounded": cot_price_pay,
                    "vhkt": vhkt_price
                },
                "payment_cycle": payment_cycle,
                "to_vt": to_vt,  # Organization/Operations Group VT1/2/3/4/5
                "site_type": site_type, # HTCS, MBF, VNPT...
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
            
        SITE_CACHE["data"] = sites_list
        SITE_CACHE["last_fetched"] = time.time()
        
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

def _vn_currency_words(amount: int) -> str:
    """Convert a positive integer VND amount to Vietnamese words."""
    ones = ['', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
    def _group(n, zero_lead):
        h, rem = divmod(n, 100)
        t, u = divmod(rem, 10)
        parts = []
        if h: parts.append(ones[h] + ' trăm')
        if t == 1:
            parts.append('mười' if u == 0 else f'mười {ones[u]}')
        elif t > 1:
            parts.append(f'{ones[t]} mươi' + (f' {ones[u]}' if u else ''))
        elif u and (h or zero_lead):
            parts.append(f'lẻ {ones[u]}')
        elif u:
            parts.append(ones[u])
        return ' '.join(parts)
    
    if amount == 0: return 'không đồng'
    result = []
    billions, remainder = divmod(abs(amount), 10**9)
    if billions: result.append(f'{_group(billions, False)} tỷ')
    millions, remainder = divmod(remainder, 10**6)
    if millions: result.append(f'{_group(millions, bool(billions))} triệu')
    thousands, remainder = divmod(remainder, 10**3)
    if thousands: result.append(f'{_group(thousands, bool(billions or millions))} nghìn')
    if remainder: result.append(_group(remainder, True))
    return ' '.join(result) + ' đồng'

def _fmt(n) -> str:
    """Format number as Vietnamese currency string (dot-separated)."""
    try: return f"{int(n):,}".replace(",", ".")
    except: return "0"

@app.post("/generate/{site_id}")
def generate_document(site_id: str, template_type: str = Body(..., embed=True)):
    """Triggers dynamic docx generation for a specific site & template type."""
    site_id = site_id.upper()
    print(f"Generating docx for: {site_id} with template {template_type}")

    def _save_progress(tpl_type, filename):
        progress_data = load_progress()
        if site_id not in progress_data:
            progress_data[site_id] = {
                "selected_template": tpl_type,
                "status": "dong_y",
                "new_contract_no": "",
                "new_contract_date": "",
                "new_price_confirmed": None,
                "progress": {"draft_prepared": True, "submitted_internal": False, "signed_and_stamped": False, "archived_doc": False}
            }
        else:
            if "progress" not in progress_data[site_id]:
                progress_data[site_id]["progress"] = {}
            progress_data[site_id]["progress"]["draft_prepared"] = True
            progress_data[site_id]["selected_template"] = tpl_type
        progress_data[site_id]["last_updated"] = datetime.now().isoformat()
        save_progress(progress_data)
        config = load_config()
        web_app_url = config.get("web_app_url", "")
        if web_app_url:
            sync_post_to_google_sheet_async(web_app_url, {site_id: progress_data[site_id]})
        return progress_data[site_id]

    if template_type in ["thanh_ly_ky_lai", "phu_luc_giam_gia", "phu_luc_gia_han", "phu_luc_giam_gia_gia_han", "thanh_ly_ky_moi", "ky_moi_hop_dong"]:
        from cloud_document_generator import generate_document_from_cloud
        try:
            sites = get_sites()
            site_data = next((s for s in sites if s["site_id"] == site_id), None)
            if not site_data:
                raise HTTPException(status_code=404, detail=f"Không tìm thấy dữ liệu cho trạm {site_id}")
                
            site_type_val = str(site_data.get("site_type", "")).strip().upper()
            # Only MBF gets MAT_BANG template
            is_mbf = "MBF" in site_type_val or "MOBIFONE" in site_type_val
            suffix = "_MAT_BANG.docx" if is_mbf else "_CSHT.docx"
            
            # Mapping logic based on user request
            if template_type == "phu_luc_giam_gia":
                tpl_name = f"PHU_LUC_GIAM_GIA{suffix}"
                prefix = "Phu_Luc_Giam_Gia"
            elif template_type == "phu_luc_gia_han":
                tpl_name = f"PHU_LUC_GIAM_GIA{suffix}" # Revert to GIAM_GIA template (patched with placeholders)
                prefix = "Phu_Luc_Gia_Han"
            elif template_type == "phu_luc_giam_gia_gia_han":
                tpl_name = f"PHU_LUC_GIAM_GIA{suffix}"
                prefix = "PL_GiamGia_GiaHan"
            elif template_type == "thanh_ly_ky_lai":
                tpl_name = f"THANH_LY_KY_LAI{suffix}"
                prefix = "Thanh_Ly_Ky_Lai"
            elif template_type == "thanh_ly_ky_moi":
                tpl_name = f"THANH_LY_KY_LAI{suffix}"
                prefix = "Thanh_Ly_Ky_Moi"
            elif template_type == "ky_moi_hop_dong":
                tpl_name = f"THANH_LY_KY_LAI{suffix}"
                prefix = "Ky_Moi_Hop_Dong"
            else:
                tpl_name = f"PHU_LUC_GIAM_GIA{suffix}"
                prefix = "Doc"
                
            template_path = os.path.join(WORKSPACE_DIR, "templates", tpl_name)
            
            success, out_filename_or_err = generate_document_from_cloud(site_data, template_path, OUTPUT_DIR, prefix, template_type)
            if success:
                prog = _save_progress(template_type, out_filename_or_err)
                return {"success": True, "filename": out_filename_or_err, "progress": prog}
            raise HTTPException(status_code=500, detail=f"Lỗi khởi tạo tài liệu: {out_filename_or_err}")
        except HTTPException:
            raise
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
