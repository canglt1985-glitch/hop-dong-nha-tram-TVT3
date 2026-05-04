import os
from flask import Flask, render_template_string, request, jsonify, send_file
import pandas as pd
from docx import Document
from datetime import datetime
from dateutil.relativedelta import relativedelta
import batch_processor as bp
from finance_service import FinanceService as fs

app = Flask(__name__)

# --- CONFIGURATION ---
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
T_DIR = os.path.join(os.path.dirname(BASE_DIR), "templates")
MASTER_DOC = os.path.join(T_DIR, "MASTER_TEMPLATE_VFINAL.docx")
O_DIR = os.path.join(BASE_DIR, "output")

if not os.path.exists(O_DIR):
    os.makedirs(O_DIR)

# Global Data Cache
DF_MASTER = None
DF_PRICE = None
SITES_CACHE = []

def load_data():
    global DF_MASTER, DF_PRICE, SITES_CACHE
    print("Loading data...")
    DF_PRICE = pd.read_excel(bp.PRICE_EXCEL, sheet_name='Chi tiết thuê trạm', header=None)
    DF_MASTER = pd.read_excel(bp.MASTER_EXCEL)
    
    sites = []
    today = datetime.now()
    for idx, row in DF_MASTER.iterrows():
        site_id = str(row.iloc[2]).strip()
        if site_id == "nan" or not site_id: continue
        
        schedule = bp.get_site_schedule(row, DF_PRICE)
        if not schedule: continue
            
        # Tính toán phân tích trạm
        periods = schedule["periods"]
        rem_cycles = len([p for p in periods if p["end"] >= today])
        
        owner_name = str(row.iloc[10]).strip()
        bank_owner = str(row.iloc[32]).strip()
        is_match = owner_name.lower() in bank_owner.lower() or bank_owner.lower() in owner_name.lower()
        match_status = "✅" if is_match else "⚠️ Lệch"
        
        needs_ext = schedule.get("original_end_contract", schedule["end_contract"]) < datetime(2026, 7, 1)
        ext_status = "🔴 Cần gia hạn" if needs_ext else "🟢 Còn hạn"

        sites.append({
            "idx": idx,
            "site_id": site_id,
            "owner": owner_name,
            "old_price": schedule["old_price"],
            "new_price": schedule["new_price"],
            "end_date": schedule["end_contract"].strftime('%d/%m/%Y'),
            "rem_cycles": rem_cycles,
            "match_status": match_status,
            "ext_status": ext_status,
            "suggested_new": bp.PHUONG_XA_MAP.get(site_id, ""),
        })
    SITES_CACHE = sites

@app.route("/")
def index():
    if not SITES_CACHE:
        load_data()
    
    html = """
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="UTF-8">
        <title>BTS Site Management - Card View</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.10.5/font/bootstrap-icons.css">
        <style>
            body { background: #f0f2f5; font-family: 'Inter', sans-serif; }
            .container { max-width: 1300px; }
            .site-card { 
                background: white; border-radius: 16px; border: none;
                transition: all 0.3s ease; box-shadow: 0 4px 12px rgba(0,0,0,0.05);
                height: 100%; position: relative; overflow: hidden;
            }
            .site-card:hover { transform: translateY(-5px); box-shadow: 0 12px 24px rgba(0,0,0,0.1); }
            .site-card::before {
                content: ''; position: absolute; top: 0; left: 0; width: 100%; height: 5px;
                background: linear-gradient(90deg, #0d6efd, #0dcaf0);
            }
            .card-header-site { border-bottom: 1px border-light; padding: 15px; }
            .badge-status { font-size: 0.75rem; padding: 5px 10px; border-radius: 20px; }
            .price-tag { font-size: 1.1rem; font-weight: 700; color: #0d6efd; }
            .exported { border: 2px solid #198754 !important; background: #f8fff9; }
            .search-box { 
                border-radius: 30px; padding: 12px 25px; border: 2px solid #e0e0e0;
                transition: 0.3s;
            }
            .search-box:focus { border-color: #0d6efd; box-shadow: 0 0 10px rgba(13,110,253,0.1); }
        </style>
    </head>
    <body class="container py-5">
        <div class="text-center mb-5">
            <h1 class="fw-bold text-dark mb-2">💎 BTS Site Portfolio</h1>
            <p class="text-muted">Quản lý hiệu quả - Tự động hóa thông minh</p>
        </div>

        <div class="row justify-content-center mb-5">
            <div class="col-md-8">
                <div class="input-group">
                    <span class="input-group-text bg-white border-end-0 border-2 rounded-start-pill ps-4">
                        <i class="bi bi-search text-primary"></i>
                    </span>
                    <input type="text" id="search" class="form-control border-start-0 border-2 rounded-end-pill search-box py-3" 
                           placeholder="Nhập Site ID, tên chủ trạm hoặc trạng thái..." onkeyup="filter()">
                </div>
            </div>
        </div>

        <div class="row g-4" id="site-list">
            {% for site in sites %}
            <div class="col-xl-4 col-md-6 site-item" data-search="{{site.site_id}} {{site.owner}} {{site.ext_status}}">
                <div class="site-card p-4" id="card-{{site.site_id}}">
                    <div class="d-flex justify-content-between align-items-start mb-3">
                        <div>
                            <span class="text-uppercase text-muted fw-bold small">Station ID</span>
                            <h3 class="mb-0 text-primary">{{ site.site_id }}</h3>
                        </div>
                        <span class="badge {{ 'bg-danger' if 'Cần gia hạn' in site.ext_status else 'bg-success' }} badge-status">
                            {{ site.ext_status }}
                        </span>
                    </div>

                    <div class="mb-3">
                        <div class="d-flex align-items-center mb-1">
                            <i class="bi bi-person-circle me-2 text-muted"></i>
                            <span class="fw-bold">{{ site.owner }}</span>
                            <span class="ms-2 small text-{{ 'success' if '✅' in site.match_status else 'danger' }}">
                                {{ site.match_status }} Tài khoản
                            </span>
                        </div>
                        <div class="text-muted small ps-4">Lịch thanh toán: <span class="badge bg-light text-dark border">{{ site.rem_cycles }} kỳ còn lại</span></div>
                    </div>

                    <div class="bg-light rounded-3 p-3 mb-4">
                        <div class="row text-center">
                            <div class="col-6 border-end">
                                <div class="small text-muted">Hạn hợp đồng</div>
                                <div class="fw-bold {{ 'text-danger' if 'Cần gia hạn' in site.ext_status else '' }}">{{ site.end_date }}</div>
                            </div>
                            <div class="col-6">
                                <div class="small text-muted">Giá thuê mới</div>
                                <div class="price-tag">{{ "{:,.0f}".format(site.new_price).replace(',','.') }}</div>
                            </div>
                        </div>
                    </div>

                    <div class="mb-3">
                        <label class="form-label small fw-bold text-muted">📍 Khu vực tự động (Xã/Thành phố)</label>
                        <input type="text" class="form-control form-control-sm rounded-pill" id="xa-{{site.site_id}}" value="{{site.suggested_new}}">
                    </div>

                    <div class="d-grid pt-2">
                        <button class="btn btn-primary rounded-pill py-2 fw-bold" onclick="exportSite('{{site.site_id}}', {{site.idx}})">
                            <i class="bi bi-file-earmark-word-fill me-2"></i> SOẠN PHỤ LỤC
                        </button>
                    </div>
                </div>
            </div>
            {% endfor %}
        </div>

        <script>
            function filter() {
                let q = document.getElementById('search').value.toLowerCase();
                document.querySelectorAll('.site-item').forEach(i => {
                    i.style.display = i.getAttribute('data-search').toLowerCase().includes(q) ? '' : 'none';
                });
            }

            async function exportSite(siteId, idx) {
                let xaMoi = document.getElementById('xa-' + siteId).value;
                let btn = document.querySelector(`#card-${siteId} button`);
                let originalHtml = btn.innerHTML;
                
                btn.disabled = true;
                btn.innerHTML = '<span class="spinner-border spinner-border-sm me-2"></span> Đang tạo file...';

                try {
                    let res = await fetch('/export', {
                        method: 'POST',
                        headers: {'Content-Type': 'application/json'},
                        body: JSON.stringify({site_id: siteId, master_idx: idx, xa_moi: xaMoi})
                    });
                    let data = await res.json();
                    if(data.success) {
                        document.getElementById('card-' + siteId).classList.add('exported');
                        btn.classList.remove('btn-primary');
                        btn.classList.add('btn-success');
                        btn.innerHTML = '<i class="bi bi-check-circle-fill me-2"></i> HOÀN THÀNH';
                        window.open('/download?path=' + encodeURIComponent(data.path));
                    } else {
                        alert("Lỗi xuất file: " + data.error);
                        btn.disabled = false;
                        btn.innerHTML = originalHtml;
                    }
                } catch(e) { 
                    alert("Lỗi kết nối server"); 
                    btn.disabled = false; 
                    btn.innerHTML = originalHtml; 
                }
            }
        </script>
    </body>
    </html>
    """
    return render_template_string(html, sites=SITES_CACHE)

@app.route("/export", methods=['POST'])
def export_api():
    data = request.json
    idx = data['master_idx']
    xa_moi = data.get('xa_moi', '').strip()
    
    try:
        row = DF_MASTER.loc[idx]
        site_id = str(row.iloc[2]).strip()
        if xa_moi:
            bp.PHUONG_XA_MAP[site_id] = xa_moi
            
        success, out_file = bp.process_site(row, DF_PRICE)
        if success:
            return jsonify({'success': True, 'path': out_file})
        else:
            return jsonify({'success': False, 'error': out_file})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)})

@app.route("/download")
def download():
    path = request.args.get('path')
    if os.path.exists(path):
        return send_file(path, as_attachment=True)
    return "File not found", 404

if __name__ == "__main__":
    load_data()
    app.run(host='0.0.0.0', port=5000, debug=False)
