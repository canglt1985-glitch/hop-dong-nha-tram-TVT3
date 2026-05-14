/* eslint-disable react-hooks/set-state-in-effect */
import { useEffect, useState, useMemo } from 'react'
import { 
  FileText, Loader2, Search, 
  Download, Layers, 
  ChevronDown, Settings, BarChart2, 
  AlertTriangle, Filter, Copy, ExternalLink, RefreshCw, Calendar
} from 'lucide-react'

import { fetchSettings, updateSettings, fetchSites, updateProgress, generateDocument } from './api/siteApi';
import { formatCurrency, isContractExpired, isCompleted, isPriceAddendumPending, isBankAccountMismatch, matchToVt, isOutOfPriceRange, isUnpaid, calculateAlignedCycles } from './utils/siteLogic';
import type { Site } from './types/site';

// --- BIỂU MẪU ĐĂNG KÝ (TEMPLATES REGISTRATION) ---
const TEMPLATE_CONFIGS = [
  { id: 'phu_luc_giam_gia', name: '1. Phụ lục giảm giá đơn giá', ready: true },
  { id: 'phu_luc_gia_han', name: '2. Phụ lục gia hạn thời gian', ready: true },
  { id: 'phu_luc_giam_gia_gia_han', name: '3. Phụ lục giảm giá & gia hạn (5 năm)', ready: true },
  { id: 'thanh_ly_ky_lai', name: '4. Phụ lục thanh lý, ký lại (5 năm)', ready: true },
  { id: 'thanh_ly_ky_moi', name: '5. Phụ lục thanh lý, ký mới (đổi chủ thể)', ready: false },
  { id: 'ky_moi_hop_dong', name: '6. Ký mới hợp đồng hoàn toàn', ready: false }
];

// --- TRẠNG THÁI TIẾN ĐỘ HỒ SƠ (PROGRESS STATUS CATEGORIES) ---
const STATUS_CATEGORIES = [
  { id: 'chua_xu_ly', name: 'Chưa chốt đàm phán', color: 'bg-slate-50 text-slate-700 border-slate-200', dot: 'bg-slate-400' },
  { id: 'dong_y', name: 'Đã đồng ý giảm giá', color: 'bg-sky-50 text-sky-700 border-sky-100', dot: 'bg-sky-500' },
  { id: 'trinh_ky_phu_luc', name: 'Đã trình ký phụ lục', color: 'bg-amber-50 text-amber-700 border-amber-100', dot: 'bg-amber-500' },
  { id: 'gia_han_5_nam', name: 'Đã gia hạn 5 năm', color: 'bg-orange-50 text-orange-700 border-orange-100', dot: 'bg-orange-500' },
  { id: 'can_thanh_ly', name: 'Cần gia hạn, tái ký', color: 'bg-rose-50 text-rose-700 border-rose-100', dot: 'bg-rose-500' },
  { id: 'da_ky_ho_so', name: 'Đã ký hồ sơ', color: 'bg-emerald-50 text-emerald-700 border-emerald-100', dot: 'bg-emerald-500' },
  { id: 'da_gui_thanh_toan', name: 'Đã gửi thanh toán', color: 'bg-indigo-50 text-indigo-700 border-indigo-100', dot: 'bg-indigo-500' }
];



function App() {
  const [sites, setSites] = useState<Site[]>([])
  const [loading, setLoading] = useState(true)
  
  // Trạm được chọn hiện hành
  const [selectedSiteId, setSelectedSiteId] = useState<string>('')
  
  // Từ khóa tìm kiếm cho bảng Master Table
  const [tableSearchQuery, setTableSearchQuery] = useState('')
  
  // Lọc tab báo cáo thống kê: 'all' | 'expired' | 'unprocessed' | 'mismatch' | 'success' | 'outOfPrice' | 'unpaid'
  const [activeAuditFilter, setActiveAuditFilter] = useState<string>('all')
  
  // Lọc theo Tổ VT: 'all' | 'VT1' | 'VT2' | 'VT3' | 'VT4' | 'VT5'
  const [selectedToVt, setSelectedToVt] = useState<string>('all')
  
  // Lọc theo Loại Trạm: 'all' | 'HTCS' | 'MBF' | 'VNPT'
  const [activeTypeFilter, setActiveTypeFilter] = useState<string>('all')
  
  const [activeMenu, setActiveMenu] = useState('Bảng điều khiển')
  const [generating, setGenerating] = useState(false)
  const [downloadFilename, setDownloadFilename] = useState<string | null>(null)
  const [savingProgress, setSavingProgress] = useState(false)
  
  // Pagination State
  const [currentPage, setCurrentPage] = useState(1)
  const ITEMS_PER_PAGE = 30

  // Các trường chỉnh sửa thông tin thực tế cho trạm đang chọn
  const [editStatus, setEditStatus] = useState('dong_y')
  const [editTemplate, setEditTemplate] = useState('thanh_ly_ky_lai')
  const [newContractNo, setNewContractNo] = useState('')
  const [newContractDate, setNewContractDate] = useState('')
  const [newPriceConfirmed, setNewPriceConfirmed] = useState<string>('')

  // Cấu hình Google Sheets settings
  const [spreadsheetId, setSpreadsheetId] = useState('19fmCxjIiY0g0bj823-QpThXL8UyYeZKAdBoCyeodv1g')
  const [webAppUrl, setWebAppUrl] = useState('')
  const [savingSettings, setSavingSettings] = useState(false)

  // Tải cấu hình và danh sách trạm từ backend
  useEffect(() => {
    fetchSettings()
      .then(data => {
        if (data.spreadsheet_id) setSpreadsheetId(data.spreadsheet_id)
        if (data.web_app_url) setWebAppUrl(data.web_app_url)
      })
      .catch(err => console.error('Lỗi tải cấu hình settings:', err))
      
    fetchSitesList()
  }, [])

  function fetchSitesList(forceRefresh: boolean = false) {
    setLoading(true)
    fetchSites(forceRefresh)
      .then((data: Site[]) => {
        setSites(data)
        if (data.length > 0) {
          const defaultSite = data.find(s => s.site_id === 'DNXL10') || data[0]
          setSelectedSiteId(defaultSite.site_id)
        }
        setLoading(false)
      })
      .catch(err => {
        console.error(err)
        setLoading(false)
      })
  }

  // Lấy chi tiết thông tin trạm đang chọn
  const selectedSite = useMemo(() => {
    return sites.find(s => s.site_id === selectedSiteId)
  }, [sites, selectedSiteId])

  // Đồng bộ giá trị input khi thay đổi trạm được chọn
  useEffect(() => {
    if (selectedSite) {
      const isSaved = !!selectedSite.progress_tracker?.last_updated
      
      // Auto-suggest Logic (Trước 30/06/2026 -> Hợp đồng mới | Sau -> Phụ lục)
      const isExpiringSoon = isContractExpired(selectedSite)
      const suggestedStatus = isExpiringSoon ? 'can_thanh_ly' : 'dong_y'
      const isMbf = (selectedSite.site_type || '').toUpperCase().includes('MBF')
      const defaultExtTemplate = isMbf ? 'phu_luc_gia_han' : 'thanh_ly_ky_lai'
      let defaultTemplate = isExpiringSoon ? defaultExtTemplate : 'phu_luc_giam_gia'

      if (isSaved) {
        setEditStatus(selectedSite.progress_tracker?.status || suggestedStatus)
        const storedTemplate = selectedSite.progress_tracker.selected_template
        if (storedTemplate === 'giam_gia_mbf_dn' || storedTemplate === 'phu_luc_giam_gia') {
          defaultTemplate = 'phu_luc_giam_gia'
        } else {
          defaultTemplate = storedTemplate || defaultTemplate
        }
      } else {
        // Chưa lưu -> Ép trạng thái và biểu mẫu gợi ý
        setEditStatus(suggestedStatus)
      }
      
      setEditTemplate(defaultTemplate)
      
      setNewContractNo(selectedSite.progress_tracker?.new_contract_no || '')
      setNewContractDate(selectedSite.progress_tracker?.new_contract_date || '')
      setNewPriceConfirmed(
        selectedSite.progress_tracker?.new_price_confirmed !== undefined && selectedSite.progress_tracker?.new_price_confirmed !== null
          ? String(selectedSite.progress_tracker.new_price_confirmed)
          : String(selectedSite.new_price)
      )
    }
  }, [selectedSite])
  
  // Tính toán chu kỳ thanh toán dựa trên logic mới (Cân đối ngày lẻ vào Kỳ 1)
  const alignedPaymentCycles = useMemo(() => {
    if (!selectedSite || !newPriceConfirmed || isNaN(parseFloat(newPriceConfirmed))) return null;
    
    // Logic: Ngày bắt đầu HĐ mới = Ngày sau ngày hết hạn cũ
    let startDateStr = '';
    try {
      if (selectedSite.end_date) {
        let expDate: Date;
        if (selectedSite.end_date.includes('/')) {
          const [d, m, y] = selectedSite.end_date.split('/').map(Number);
          expDate = new Date(y, m - 1, d);
        } else {
          // Assume ISO YYYY-MM-DD
          expDate = new Date(selectedSite.end_date);
        }
        
        if (!isNaN(expDate.getTime())) {
          expDate.setDate(expDate.getDate() + 1);
          startDateStr = expDate.toLocaleDateString('en-GB');
        } else {
          startDateStr = '01/01/2026';
        }
      } else {
        startDateStr = '01/01/2026';
      }
    } catch {
      startDateStr = '01/01/2026';
    }

    const cycleMonths = 6; 
    const termYears = 5;   
    const monthlyPrice = parseFloat(newPriceConfirmed);
    
    return calculateAlignedCycles(startDateStr, cycleMonths, termYears, monthlyPrice);
  }, [selectedSite, newPriceConfirmed]);


  // Thống kê số lượng (Có thể áp dụng filter Tổ VT động để nhìn số liệu cực kỳ trực quan)
  const statsCounts = useMemo(() => {
    let all = 0
    let expired = 0
    let unaddended = 0
    let mismatch = 0
    let success = 0
    let outOfPrice = 0
    let unpaid = 0

    sites.forEach(s => {
      // Áp dụng bộ lọc Tổ VT đang chọn bằng hàm matchToVt thông minh
      if (selectedToVt !== 'all') {
        if (!matchToVt(s.to_vt, selectedToVt)) return
      }

      all++
      if (isContractExpired(s)) expired++
      if (isPriceAddendumPending(s)) unaddended++
      if (isBankAccountMismatch(s)) mismatch++
      if (isCompleted(s)) success++
      if (isOutOfPriceRange(s)) outOfPrice++
      if (isUnpaid(s)) unpaid++
    })

    return {
      all,
      expired,
      unaddended,
      mismatch,
      success,
      outOfPrice,
      unpaid
    }
  }, [sites, selectedToVt])

  // Thống kê tỷ lệ đạt mục tiêu đàm phán (cột reached_target = 'Đạt')
  const targetStats = useMemo(() => {
    let totalNegotiated = 0
    let reachedCount = 0

    sites.forEach(s => {
      if (selectedToVt !== 'all') {
        if (!matchToVt(s.to_vt, selectedToVt)) return
      }

      if (s.has_agreed_1245) {
        totalNegotiated++
        if (s.reached_target === 'Đạt') {
          reachedCount++
        }
      }
    })

    const pct = totalNegotiated > 0 ? Math.round((reachedCount / totalNegotiated) * 100) : 0
    return {
      total: totalNegotiated,
      reached: reachedCount,
      pct
    }
  }, [sites, selectedToVt])

  // Lọc và tìm kiếm danh sách trạm hiển thị trong Master Table
  const filteredSites = useMemo(() => {
    return sites.filter(s => {
      // 1. Lọc theo Tổ VT được chọn bằng hàm matchToVt thông minh
      if (selectedToVt !== 'all') {
        if (!matchToVt(s.to_vt, selectedToVt)) return false
      }

      // 2. Lọc theo bộ lọc quản trị / trạng thái tiến độ
      if (activeAuditFilter === 'expired' && !isContractExpired(s)) return false
      if (activeAuditFilter === 'unprocessed' && !isPriceAddendumPending(s)) return false
      if (activeAuditFilter === 'mismatch' && !isBankAccountMismatch(s)) return false
      if (activeAuditFilter === 'success' && !isCompleted(s)) return false
      if (activeAuditFilter === 'outOfPrice' && !isOutOfPriceRange(s)) return false
      if (activeAuditFilter === 'unpaid' && !isUnpaid(s)) return false

      // 2b. Lọc theo Loại Trạm (HTCS, MBF, v.v.)
      if (activeTypeFilter !== 'all') {
        const siteType = (s.site_type || '').toUpperCase()
        const filterType = activeTypeFilter.toUpperCase()
        
        // Smart match: MBF matches MOBIFONE
        const isMbfMatch = (filterType === 'MBF' && (siteType.includes('MBF') || siteType.includes('MOBIFONE')))
        const isOtherMatch = siteType.includes(filterType)
        
        if (!(isMbfMatch || isOtherMatch)) return false
      }

      // 3. Lọc theo từ khóa tìm kiếm (Mã trạm, tên chủ trạm, chủ tài khoản)
      if (tableSearchQuery) {
        const query = tableSearchQuery.toLowerCase().trim()
        const matchId = s.site_id.toLowerCase().includes(query)
        const matchOwner = s.owner.toLowerCase().includes(query)
        const matchBank = s.banking_info?.account_owner?.toLowerCase().includes(query)
        const matchVt = s.to_vt?.toLowerCase().includes(query)
        return matchId || matchOwner || matchBank || matchVt
      }

      return true
    })
  }, [sites, activeAuditFilter, selectedToVt, activeTypeFilter, tableSearchQuery])

  // Reset pagination khi bộ lọc thay đổi
  useEffect(() => {
    setCurrentPage(1)
  }, [activeAuditFilter, selectedToVt, activeTypeFilter, tableSearchQuery])

  // Dữ liệu phân trang
  const paginatedSites = useMemo(() => {
    const start = (currentPage - 1) * ITEMS_PER_PAGE
    return filteredSites.slice(start, start + ITEMS_PER_PAGE)
  }, [filteredSites, currentPage])

  const totalPages = Math.ceil(filteredSites.length / ITEMS_PER_PAGE)

  // Thống kê chi tiết theo Tổ Viễn Thông (Tổ VT)
  const vtStats = useMemo(() => {
    const groups: { [key: string]: { total: number; expired: number; unaddended: number; mismatch: number; success: number } } = {}
    
    sites.forEach(s => {
      const vt = s.to_vt || 'Chưa rõ'
      if (!groups[vt]) {
        groups[vt] = { total: 0, expired: 0, unaddended: 0, mismatch: 0, success: 0 }
      }
      groups[vt].total++
      if (isContractExpired(s)) groups[vt].expired++
      if (isPriceAddendumPending(s)) groups[vt].unaddended++
      if (isBankAccountMismatch(s)) groups[vt].mismatch++
      if (isCompleted(s)) groups[vt].success++
    })
    
    return Object.entries(groups).map(([name, val]) => ({
      name,
      ...val,
      pct: Math.round((val.success / val.total) * 100) || 0
    })).sort((a, b) => b.total - a.total)
  }, [sites])

  // Lưu thông tin cập nhật tiến độ & dữ liệu đàm phán xuống file progress_tracker.json cục bộ
  const saveChangesToServer = () => {
    if (!selectedSite) return
    setSavingProgress(true)

    const updatedProgress = { ...selectedSite.progress_tracker.progress }
    const payload = {
      site_id: selectedSite.site_id,
      selected_template: editTemplate,
      status: editStatus,
      progress: updatedProgress,
      new_contract_no: newContractNo,
      new_contract_date: newContractDate,
      new_price_confirmed: newPriceConfirmed ? parseFloat(newPriceConfirmed) : undefined
    }

    updateProgress(payload)
    .then(data => {
      setSavingProgress(false)
      if (data.success) {
        setSites(prev => prev.map(s => {
          if (s.site_id === selectedSite.site_id) {
            return {
              ...s,
              progress_tracker: {
                selected_template: editTemplate,
                status: editStatus,
                new_contract_no: newContractNo,
                new_contract_date: newContractDate,
                new_price_confirmed: newPriceConfirmed ? parseFloat(newPriceConfirmed) : undefined,
                progress: updatedProgress
              }
            }
          }
          return s
        }))
        alert('Đã cập nhật tiến độ & thông tin đàm phán thành công!')
      }
    })
    .catch(err => {
      setSavingProgress(false)
      console.error('Lỗi đồng bộ tiến độ:', err)
      alert('Không thể lưu tiến độ lên máy chủ!')
    })
  }

  // Tích chọn nhanh các bước trình ký và đồng bộ hóa thông minh trạng thái tiến độ thực tế
  const toggleStep = (stepKey: 'draft_prepared' | 'submitted_internal' | 'signed_and_stamped' | 'archived_doc') => {
    if (!selectedSite) return
    const updatedProgress = { 
      ...selectedSite.progress_tracker.progress,
      [stepKey]: !selectedSite.progress_tracker.progress[stepKey]
    }
    
    // Tự động xác định trạng thái tổng dựa trên nấc tiến trình cao nhất được tích chọn
    let autoStatus = editStatus
    if (updatedProgress.archived_doc) {
      autoStatus = 'da_gui_thanh_toan'
    } else if (updatedProgress.signed_and_stamped) {
      autoStatus = 'da_ky_ho_so'
    } else if (updatedProgress.submitted_internal) {
      autoStatus = 'trinh_ky_phu_luc'
    } else if (updatedProgress.draft_prepared) {
      autoStatus = 'dong_y'
    } else {
      // Nếu không tích chọn bước nào, quay về mặc định
      autoStatus = isContractExpired(selectedSite) ? 'can_thanh_ly' : 'dong_y'
    }
    
    setEditStatus(autoStatus)
    
    updateProgress({
        site_id: selectedSite.site_id,
        selected_template: editTemplate,
        status: autoStatus,
        progress: updatedProgress,
        new_contract_no: newContractNo,
        new_contract_date: newContractDate,
        new_price_confirmed: newPriceConfirmed ? parseFloat(newPriceConfirmed) : undefined
    })
    .then(data => {
      if (data.success) {
        setSites(prev => prev.map(s => {
          if (s.site_id === selectedSite.site_id) {
            return {
              ...s,
              progress_tracker: {
                ...s.progress_tracker,
                status: autoStatus,
                progress: updatedProgress
              }
            }
          }
          return s
        }))
      }
    })
    .catch(err => console.error('Lỗi tích bước tiến trình:', err))
  }

  // Lưu cấu hình Google Sheets cài đặt hệ thống
  const handleSaveSettings = () => {
    setSavingSettings(true)
    updateSettings({
        spreadsheet_id: spreadsheetId,
        web_app_url: webAppUrl
      })
    .then(data => {
      setSavingSettings(false)
      if (data.success) {
        alert('Đã cấu hình thông tin Google Sheets thành công!')
        fetchSitesList()
      }
    })
    .catch(err => {
      setSavingSettings(false)
      console.error(err)
      alert('Lỗi lưu cài đặt hệ thống!')
    })
  }

  // Sinh tệp Word (.docx) điền dữ liệu tự động
  const handleGenerate = () => {
    if (!selectedSite) return
    setGenerating(true)
    setDownloadFilename(null)

    generateDocument(selectedSite.site_id, editTemplate)
    .then(data => {
      if (data.success) {
        setDownloadFilename(data.filename)
        setSites(prev => prev.map(s => {
          if (s.site_id === selectedSite.site_id) {
            return {
              ...s,
              progress_tracker: {
                ...data.progress,
                new_contract_no: newContractNo,
                new_contract_date: newContractDate,
                new_price_confirmed: newPriceConfirmed ? parseFloat(newPriceConfirmed) : undefined
              }
            }
          }
          return s
        }))
      }
      setGenerating(false)
    })
    .catch(err => {
      alert(err.message || 'Lỗi phát sinh trong quá trình soạn file Word!')
      setGenerating(false)
    })
  }

  // Mã nguồn Apps Script để copy-paste
  const appsScriptCode = `// Google Apps Script dán vào Extensions -> Apps Script của bạn
function doGet(e) {
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("tien do");
  if (!sheet) {
    sheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet("tien do");
    sheet.appendRow(["site_id", "selected_template", "status", "draft_prepared", "submitted_internal", "signed_and_stamped", "archived_doc", "new_contract_no", "new_contract_date", "new_price_confirmed", "last_updated"]);
  }
  var data = sheet.getDataRange().getValues();
  var headers = data[0];
  var rows = [];
  for (var i = 1; i < data.length; i++) {
    var row = {};
    for (var j = 0; j < headers.length; j++) {
      row[headers[j]] = data[i][j];
    }
    rows.push(row);
  }
  return ContentService.createTextOutput(JSON.stringify(rows))
    .setMimeType(ContentService.MimeType.JSON);
}

function doPost(e) {
  try {
    var payload = JSON.parse(e.postData.contents);
    var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName("tien do");
    if (!sheet) {
      sheet = SpreadsheetApp.getActiveSpreadsheet().insertSheet("tien do");
      sheet.appendRow(["site_id", "selected_template", "status", "draft_prepared", "submitted_internal", "signed_and_stamped", "archived_doc", "new_contract_no", "new_contract_date", "new_price_confirmed", "last_updated"]);
    }
    
    var dataRange = sheet.getDataRange();
    var values = dataRange.getValues();
    var headers = values[0];
    
    var siteRowMap = {};
    for (var i = 1; i < values.length; i++) {
      siteRowMap[values[i][0]] = i + 1;
    }
    
    for (var siteId in payload) {
      var record = payload[siteId];
      var rowData = [];
      for (var colIdx = 0; colIdx < headers.length; colIdx++) {
        var header = headers[colIdx];
        if (header === "site_id") rowData.push(siteId);
        else if (header === "selected_template") rowData.push(record.selected_template || "");
        else if (header === "status") rowData.push(record.status || "");
        else if (header === "draft_prepared") rowData.push(record.progress?.draft_prepared ? "TRUE" : "FALSE");
        else if (header === "submitted_internal") rowData.push(record.progress?.submitted_internal ? "TRUE" : "FALSE");
        else if (header === "signed_and_stamped") rowData.push(record.progress?.signed_and_stamped ? "TRUE" : "FALSE");
        else if (header === "archived_doc") rowData.push(record.progress?.archived_doc ? "TRUE" : "FALSE");
        else if (header === "new_contract_no") rowData.push(record.new_contract_no || "");
        else if (header === "new_contract_date") rowData.push(record.new_contract_date || "");
        else if (header === "new_price_confirmed") rowData.push(record.new_price_confirmed || "");
        else if (header === "last_updated") rowData.push(record.last_updated || new Date().toISOString());
        else rowData.push("");
      }
      
      var rowNum = siteRowMap[siteId];
      if (rowNum) {
        sheet.getRange(rowNum, 1, 1, headers.length).setValues([rowData]);
      } else {
        sheet.appendRow(rowData);
      }
    }
    
    return ContentService.createTextOutput(JSON.stringify({status: "success", message: "Đồng bộ tiến độ thành công!"}))
      .setMimeType(ContentService.MimeType.JSON);
  } catch (err) {
    return ContentService.createTextOutput(JSON.stringify({status: "error", message: err.toString()}))
      .setMimeType(ContentService.MimeType.JSON);
  }
}`;

  return (
    <div className="flex h-screen bg-[#F8FAFC] text-[#1E293B] font-sans overflow-hidden">
      
      {/* 1. SIDEBAR TRÁI */}
      <aside className="w-[270px] bg-white border-r border-[#E2E8F0] flex flex-col justify-between h-full select-none shrink-0 shadow-sm">
        <div className="flex flex-col">
          <div className="flex items-center gap-3 px-6 py-5 border-b border-[#F1F5F9]">
            <div className="w-8.5 h-8.5 rounded-xl bg-gradient-to-tr from-blue-600 to-indigo-600 flex items-center justify-center shadow-md shadow-blue-500/10">
              <FileText className="w-4.5 h-4.5 text-white" />
            </div>
            <div>
              <h2 className="text-sm font-extrabold tracking-tight text-slate-800 leading-none">BTS Contract</h2>
              <p className="text-[10px] text-blue-600 font-bold mt-1">Hệ Thống Quản Trị & Đối Soát</p>
            </div>
          </div>

          <nav className="p-4 space-y-1">
            {[
              { name: 'Bảng điều khiển', icon: Layers },
              { name: 'Báo cáo thống kê', icon: BarChart2 },
              { name: 'Cài đặt hệ thống', icon: Settings },
            ].map(item => {
              const Icon = item.icon
              const isActive = activeMenu === item.name
              return (
                <button
                  key={item.name}
                  onClick={() => setActiveMenu(item.name)}
                  className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl text-xs font-bold transition-all cursor-pointer ${isActive ? 'bg-blue-50/70 text-blue-600 border border-blue-100/50' : 'text-slate-500 hover:text-slate-800 hover:bg-slate-50'}`}
                >
                  <Icon className={`w-4 h-4 ${isActive ? 'text-blue-600' : 'text-slate-400'}`} />
                  {item.name}
                </button>
              )
            })}
          </nav>
        </div>

        <div className="p-4 border-t border-[#F1F5F9] bg-slate-50/60">
          <div className="flex items-center justify-between w-full">
            <div className="flex items-center gap-3">
              <div className="relative">
                <div className="w-9 h-9 rounded-full bg-gradient-to-tr from-blue-500 to-teal-400 flex items-center justify-center font-bold text-white text-xs border border-slate-200">
                  QT
                </div>
                <span className="absolute bottom-0 right-0 w-2.5 h-2.5 bg-emerald-500 border-2 border-white rounded-full" />
              </div>
              <div className="text-left">
                <h4 className="text-xs font-black text-slate-800 leading-none">Quản trị viên</h4>
                <p className="text-[10px] text-slate-400 font-bold mt-0.5">Phòng Đàm Phán Ký Kết</p>
              </div>
            </div>
          </div>
        </div>
      </aside>

      {/* 2. MAIN WORKSPACE */}
      <div className="flex-1 flex flex-col h-full overflow-hidden">
        
        {/* TOP BAR */}
        <header className="h-[64px] bg-white border-b border-[#E2E8F0] flex items-center justify-between px-8 shrink-0">
          <div className="flex items-center gap-2">
            <Layers className="w-5 h-5 text-blue-600" />
            <h1 className="text-sm font-black text-slate-800 uppercase">Hệ thống đàm phán & đối soát hợp đồng BTS</h1>
          </div>

          <div className="flex items-center gap-5">
            <button 
              onClick={() => fetchSitesList(true)} 
              title="Đồng bộ lại từ Google Sheets / Excel (Bỏ qua Cache)"
              className="flex items-center gap-1.5 px-3 py-1.5 bg-slate-100 hover:bg-slate-200 text-[10px] font-black uppercase text-slate-700 rounded-lg transition-colors cursor-pointer border border-slate-200"
            >
              <RefreshCw className="w-3.5 h-3.5" />
              Đồng bộ dữ liệu
            </button>
            <div className="w-px h-6 bg-slate-200" />
            <div className="flex items-center gap-3 select-none">
              <div className="w-8 h-8 rounded-full bg-gradient-to-tr from-pink-500 to-rose-500 flex items-center justify-center font-black text-white text-xs border border-white shadow-sm">
                S
              </div>
              <span className="text-xs font-extrabold text-slate-700">Tổ Đàm Phán Kỹ Thuật</span>
            </div>
          </div>
        </header>

        {loading ? (
          <div className="flex-1 flex flex-col items-center justify-center gap-3 text-slate-400 bg-slate-50">
            <Loader2 className="w-8 h-8 animate-spin text-blue-500" />
            <span className="text-xs font-extrabold">Đang kết nối dữ liệu đám mây Google Sheets và phân tích chỉ số chất lượng...</span>
          </div>
        ) : (
          <div className="flex-1 flex overflow-hidden">
            
            {/* VIEW 1: BẢNG ĐIỀU KHIỂN CHÍNH */}
            {activeMenu === 'Bảng điều khiển' && (
              <>
                {/* PHẦN TRÁI (65%): BÁO CÁO THỐNG KÊ CHẤT LƯỢNG & BẢNG MASTER TABLE */}
                <div className="w-2/3 h-full overflow-y-auto p-6 space-y-5 border-r border-[#E2E8F0]">
                  
                  {/* Đã xóa các bộ lọc bự ở đây để nhường chỗ cho Table Header Filters */}

                  {/* KHU VỰC DANH SÁCH MASTER AUDIT TABLE (BảngMaster đối soát) */}
                  <div className="bg-white rounded-2xl border border-[#E2E8F0] p-5 shadow-sm space-y-4">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-3">
                      <div>
                        <h2 className="text-xs font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                          <Filter className="w-4 h-4 text-blue-600" />
                          Danh sách trạm đối soát (Tìm thấy: {filteredSites.length} trạm)
                        </h2>
                        <p className="text-[10px] text-slate-400 mt-1">Bấm vào hàng của trạm để hiển thị bảng điều chỉnh thông tin và xuất sinh tệp Word tương ứng bên phải</p>
                      </div>

                      {/* Thanh tìm kiếm nhanh trong bảng */}
                      <div className="relative w-72">
                        <Search className="absolute left-3 top-2.5 w-3.5 h-3.5 text-slate-400" />
                        <input 
                          type="text"
                          placeholder="Tìm kiếm mã, chủ trạm, tài khoản, tổ..."
                          value={tableSearchQuery}
                          onChange={e => setTableSearchQuery(e.target.value)}
                          className="w-full bg-slate-50 text-[11px] text-slate-700 pl-8 pr-3 py-2 rounded-xl border border-slate-200 focus:outline-none focus:border-blue-500 focus:bg-white transition-all shadow-inner"
                        />
                      </div>
                    </div>

                    {/* Thanh công cụ lọc: Filter Bar */}
                    <div className="flex flex-wrap items-center gap-3 py-1">
                      {/* Tổ VT Filter */}
                      <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg p-1 shadow-sm">
                        <span className="text-[10px] font-bold text-slate-500 pl-2">Tổ:</span>
                        {['all', 'VT1', 'VT2', 'VT3', 'VT4', 'VT5'].map(vt => (
                          <button 
                            key={vt}
                            onClick={() => setSelectedToVt(vt)}
                            className={`px-2 py-1 text-[10px] font-black rounded transition-all ${selectedToVt === vt ? 'bg-blue-600 text-white shadow' : 'text-slate-600 hover:bg-slate-200'}`}
                          >
                            {vt === 'all' ? 'Tất cả' : vt}
                          </button>
                        ))}
                      </div>

                      {/* Loại Trạm Filter */}
                      <div className="flex items-center gap-1.5 bg-slate-50 border border-slate-200 rounded-lg p-1 shadow-sm">
                        <span className="text-[10px] font-bold text-slate-500 pl-2">Loại:</span>
                        {['all', 'HTCS', 'MBF', 'VNPT'].map(type => (
                          <button 
                            key={type}
                            onClick={() => setActiveTypeFilter(type)}
                            className={`px-2 py-1 text-[10px] font-black rounded transition-all ${activeTypeFilter === type ? 'bg-blue-600 text-white shadow' : 'text-slate-600 hover:bg-slate-200'}`}
                          >
                            {type === 'all' ? 'Tất cả' : type}
                          </button>
                        ))}
                      </div>

                      {/* Tình trạng Filter */}
                      <div className="flex items-center gap-1.5 bg-blue-50 border border-blue-200 rounded-lg p-1 shadow-sm">
                        <span className="text-[10px] font-bold text-blue-800 pl-2">Tình trạng:</span>
                        <select 
                          value={activeAuditFilter}
                          onChange={e => setActiveAuditFilter(e.target.value)}
                          className="bg-transparent text-[10px] font-black text-blue-900 outline-none cursor-pointer pr-2 py-1"
                        >
                          <option value="all">Tất cả ({statsCounts.all})</option>
                          <option value="expired">⚠️ Cần gia hạn ({statsCounts.expired})</option>
                          <option value="unprocessed">⚙️ Đồng ý, chưa PL ({statsCounts.unaddended})</option>
                          <option value="success">✅ Đã hoàn tất ({statsCounts.success})</option>
                          <option value="outOfPrice">💰 Ngoài khung giá ({statsCounts.outOfPrice})</option>
                          <option value="mismatch">⚖️ Lệch tài khoản ({statsCounts.mismatch})</option>
                          <option value="unpaid">💸 Chưa thanh toán ({statsCounts.unpaid})</option>
                        </select>
                      </div>
                    </div>

                    {/* Master Table */}
                    <div className="overflow-x-auto border border-slate-100 rounded-xl max-h-[500px] overflow-y-auto mt-2">
                      <table className="w-full text-left border-collapse">
                        <thead className="bg-slate-50 sticky top-0 z-10">
                          <tr className="border-b border-slate-200 text-[10px] font-black text-slate-500 uppercase tracking-wider bg-slate-100">
                            <th className="p-3 pl-4">Mã Trạm</th>
                            <th className="p-3">Tổ</th>
                            <th className="p-3">Bên Cho Thuê</th>
                            <th className="p-3">Hạn HĐ Gốc</th>
                            <th className="p-3">Giá Đàm Phán</th>
                            <th className="p-3">Tiến độ & Đối soát</th>
                          </tr>
                        </thead>
                        <tbody className="text-[11px] font-bold text-slate-700 divide-y divide-slate-100">
                          {paginatedSites.length === 0 ? (
                            <tr>
                              <td colSpan={6} className="text-center py-8 text-slate-400 italic">
                                Không tìm thấy trạm nào khớp điều kiện lọc hiện hành
                              </td>
                            </tr>
                          ) : (
                            paginatedSites.map((s, index) => {
                              const isSelected = s.site_id === selectedSiteId
                              const expired = isContractExpired(s)
                              const unmatchedBank = isBankAccountMismatch(s)
                              const currentStatusCat = STATUS_CATEGORIES.find(cat => cat.id === (s.progress_tracker?.status || 'dong_y'))
                              const completed = isCompleted(s)

                              return (
                                <tr
                                  key={`${s.site_id}-${index}`}
                                  onClick={() => {
                                    setSelectedSiteId(s.site_id)
                                    setDownloadFilename(null)
                                  }}
                                  className={`hover:bg-blue-50/30 transition-all cursor-pointer ${isSelected ? 'bg-blue-50/60 border-l-4 border-l-blue-600' : ''}`}
                                >
                                  {/* 1. Mã Trạm */}
                                  <td className="p-3 pl-4">
                                    <span className="font-extrabold text-blue-600 text-xs block">{s.site_id}</span>
                                    <div className="mt-1 flex items-center gap-1.5">
                                      {s.site_type && (
                                        <span className="px-1 py-0.5 rounded text-[8px] bg-slate-100 text-slate-500 border border-slate-200 font-bold uppercase tracking-wider">
                                          {s.site_type}
                                        </span>
                                      )}
                                      {s.progress_tracker?.status === 'gia_han_5_nam' && (
                                        <span className="text-amber-500 text-[10px] flex items-center gap-0.5 font-bold"><span title="Đã gia hạn 5 năm">🌟</span></span>
                                      )}
                                    </div>
                                  </td>
                                  
                                  {/* 2. Tổ */}
                                  <td className="p-3 text-slate-500 text-[10px] font-bold">{s.to_vt || 'Chưa rõ'}</td>
                                  
                                  {/* 3. Chủ Nhà */}
                                  <td className="p-3 max-w-[120px]">
                                    <div className="text-slate-800 font-extrabold text-[11px] truncate" title={s.owner}>{s.owner}</div>
                                  </td>

                                  {/* 4. Hạn HĐ Gốc */}
                                  <td className="p-3">
                                    <span className="text-[10px] font-bold">{s.end_date || 'Chưa rõ'}</span>
                                    {expired && <span className="block mt-0.5 text-[9px] text-rose-500 font-black">⚠️ Hết hạn</span>}
                                  </td>

                                  {/* 5. Giá & Trạng Thái Đàm Phán */}
                                  <td className="p-3">
                                    {s.has_agreed_1245 ? (
                                      <div className="flex flex-col gap-0.5">
                                        <div className="flex items-center gap-1.5 text-[10px] font-black">
                                          <span className="text-slate-400 line-through">{(s.old_price / 1000000).toFixed(1)}M</span>
                                          <span className="text-slate-300">→</span>
                                          <span className="text-emerald-600">{(s.reduced_price! / 1000000).toFixed(1)}M</span>
                                        </div>
                                        {s.no_addendum_needed ? (
                                          <span className="text-[8.5px] text-blue-500 font-black">ℹ️ Không cần PL</span>
                                        ) : (
                                          <span className="text-[8.5px] text-amber-500 font-black">✨ Đã đồng ý giảm</span>
                                        )}
                                      </div>
                                    ) : (
                                      <div className="text-[10px] font-black text-slate-500">{(s.old_price / 1000000).toFixed(1)}M</div>
                                    )}
                                  </td>

                                  {/* 6. Tiến độ hồ sơ & Tài khoản */}
                                  <td className="p-3 flex flex-col items-start gap-1.5">
                                    <span className={`text-[9px] px-2 py-0.5 rounded-full border font-black ${completed ? 'bg-emerald-500 text-white border-emerald-500 shadow-sm' : currentStatusCat?.color}`}>
                                      {completed ? '✅ Đã hoàn thành' : currentStatusCat?.name}
                                    </span>
                                    
                                    {unmatchedBank && (
                                      <span className="text-[8.5px] bg-rose-50 text-rose-600 border border-rose-100 px-1.5 py-0.5 rounded font-black flex items-center gap-0.5">
                                        <AlertTriangle className="w-2.5 h-2.5 text-rose-500 shrink-0" /> Lệch TK
                                      </span>
                                    )}
                                  </td>
                                </tr>
                              )
                            })
                          )}
                        </tbody>
                      </table>
                      
                      {/* PAGINATION CONTROLS */}
                      {totalPages > 1 && (
                        <div className="flex justify-between items-center px-4 py-3 bg-slate-50 border-t border-slate-200 text-xs font-medium">
                          <span className="text-slate-500">
                            Đang xem {((currentPage - 1) * ITEMS_PER_PAGE) + 1} - {Math.min(currentPage * ITEMS_PER_PAGE, filteredSites.length)} / {filteredSites.length} trạm
                          </span>
                          <div className="flex items-center gap-2">
                            <button
                              disabled={currentPage === 1}
                              onClick={() => setCurrentPage(p => Math.max(1, p - 1))}
                              className="px-2.5 py-1 rounded bg-white border border-slate-200 text-slate-600 disabled:opacity-50 hover:bg-slate-100 transition-colors"
                            >
                              Trang trước
                            </button>
                            <span className="text-slate-700 font-bold bg-slate-200/50 px-3 py-1 rounded">
                              {currentPage} / {totalPages}
                            </span>
                            <button
                              disabled={currentPage === totalPages}
                              onClick={() => setCurrentPage(p => Math.min(totalPages, p + 1))}
                              className="px-2.5 py-1 rounded bg-white border border-slate-200 text-slate-600 disabled:opacity-50 hover:bg-slate-100 transition-colors"
                            >
                              Trang sau
                            </button>
                          </div>
                        </div>
                      )}
                    </div>
                  </div>
                </div>

                {/* PHẦN PHẢI (35%): THAO TÁC CẬP NHẬT THÔNG TIN VÀ XUẤT SOẠN BIỂU MẪU */}
                <div className="w-1/3 h-full overflow-y-auto p-6 bg-white space-y-4 flex flex-col justify-between">
                  
                  {selectedSite ? (
                    <div className="space-y-4 flex-1 flex flex-col justify-between">
                      
                      {/* Tên Trạm & Bên Cho Thuê */}
                      <div className="space-y-3 pb-3 border-b border-slate-100">
                        <div>
                          <span className="text-[10px] text-indigo-600 font-black uppercase tracking-widest block">Tổ Viễn Thông: {selectedSite.to_vt || 'Chưa rõ'}</span>
                          <h2 className="text-base font-black text-slate-800 mt-1 flex items-center gap-1.5">
                            <span className="text-blue-600">{selectedSite.site_id}</span> - {selectedSite.owner}
                          </h2>
                        </div>
                        
                        {/* 1. THÔNG TIN CHỦ TRẠM & THỜI GIAN THUÊ & CHU KỲ */}
                        <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/60 text-[11px] font-bold text-slate-600 space-y-1.5 text-left">
                          <div>
                            👤 <span className="text-slate-400 font-semibold">Chủ trạm:</span> <span className="text-slate-800">{selectedSite.owner}</span>
                          </div>
                          <div>
                            📅 <span className="text-slate-400 font-semibold">Thời gian thuê gốc:</span> <span className="text-slate-800">{selectedSite.end_date || 'Chưa rõ'}</span>
                          </div>
                          <div>
                            ⏳ <span className="text-slate-400 font-semibold">Chu kỳ thanh toán:</span> <span className="text-slate-800">{selectedSite.payment_cycle || '6 tháng'}</span>
                          </div>
                        </div>

                        {/* 2. THÔNG TIN GIÁ THUÊ (SO SÁNH KHUNG VÀ THỰC TẾ) */}
                        <div className="flex flex-col gap-2">
                          {/* KHUNG GIÁ YÊU CẦU */}
                          <div className="bg-slate-50 p-3 rounded-xl border border-slate-200/60 text-[11px] font-bold text-slate-600 space-y-1.5 text-left">
                            <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block mb-1">🏦 HẠNG MỤC GIÁ THUÊ (YÊU CẦU):</span>
                            <div className="grid grid-cols-2 gap-y-1 gap-x-2 text-[10.5px]">
                              {selectedSite.prices_breakdown.mb > 0 && (
                                <div>🏢 <span className="text-slate-400 font-semibold">Mặt bằng:</span> <span className="text-slate-800 font-black">{formatCurrency(selectedSite.prices_breakdown.mb)}</span></div>
                              )}
                              {selectedSite.prices_breakdown.pm > 0 && (
                                <div>📦 <span className="text-slate-400 font-semibold">Phòng máy:</span> <span className="text-slate-800 font-black">{formatCurrency(selectedSite.prices_breakdown.pm)}</span></div>
                              )}
                              {selectedSite.prices_breakdown.mfd > 0 && (
                                <div>⚡ <span className="text-slate-400 font-semibold">MPĐ:</span> <span className="text-slate-800 font-black">{formatCurrency(selectedSite.prices_breakdown.mfd)}</span></div>
                              )}
                              {selectedSite.prices_breakdown.cot > 0 && (
                                <div>🗼 <span className="text-slate-400 font-semibold">Cột anten:</span> <span className="text-slate-800 font-black">{formatCurrency(selectedSite.prices_breakdown.cot)}</span></div>
                              )}
                              {selectedSite.prices_breakdown.giam_tru !== 0 && (
                                <div className="col-span-2 text-rose-600">📉 <span className="text-slate-400 font-semibold">Giảm trừ:</span> <span className="font-black">{formatCurrency(selectedSite.prices_breakdown.giam_tru)}</span></div>
                              )}
                            </div>
                          </div>

                          {/* GIÁ ĐÃ THOẢ THUẬN */}
                          <div className="bg-emerald-50/50 p-3 rounded-xl border border-emerald-100 text-[11px] font-bold text-slate-600 space-y-1.5 text-left">
                            <span className="text-[10px] font-black text-emerald-600 uppercase tracking-widest block mb-1">🤝 KẾT QUẢ ĐÀM PHÁN:</span>
                            <div className="flex justify-between items-center text-xs">
                              <span className="text-slate-500 font-extrabold">Đơn giá gốc:</span>
                              <span className="text-slate-800 font-black">{formatCurrency(selectedSite.old_price)}</span>
                            </div>
                            <div className="flex justify-between items-center text-xs mt-1">
                              <span className="text-emerald-600 font-extrabold">Giá sau đàm phán:</span>
                              <span className="text-emerald-600 font-black">{formatCurrency(selectedSite.new_price)}</span>
                            </div>
                            
                            {(selectedSite.no_addendum_needed || (selectedSite.old_price > 0 && selectedSite.new_price > 0 && selectedSite.old_price <= selectedSite.new_price)) && (
                              <div className="mt-2.5 p-2 bg-indigo-50 border border-indigo-100 text-indigo-700 rounded-lg text-[9.5px] font-black leading-relaxed flex items-start gap-1.5 animate-pulse">
                                <span className="text-indigo-500">ℹ️</span>
                                <span>Trạm không cần làm phụ lục giảm giá (Giá hiện tại HT &lt;= Giá mục tiêu MT).</span>
                              </div>
                            )}

                            {(selectedSite.reached_target && (selectedSite.reached_target.toLowerCase().includes('không') || selectedSite.reached_target.toLowerCase().includes('chưa'))) && (
                              <div className="mt-2.5 p-2 bg-rose-50 border border-rose-100 text-rose-700 rounded-lg text-[9.5px] font-black leading-relaxed flex items-start gap-1.5">
                                <span className="text-rose-500">⚠️</span>
                                <span>Trạm đàm phán CHƯA ĐẠT MỤC TIÊU. Không đủ điều kiện xuất phụ lục giảm giá.</span>
                              </div>
                            )}
                          </div>
                        </div>


                        
                        {/* 3b. CHU KỲ THANH TOÁN DỰ KIẾN (HIỂN THỊ RÕ NÉT) */}
                        {alignedPaymentCycles && (
                          <div className="bg-white p-4 rounded-2xl border-2 border-blue-100 shadow-xl space-y-4">
                            <div className="flex justify-between items-center pb-2 border-b border-blue-50">
                              <span className="text-[11px] font-black text-blue-800 uppercase tracking-widest flex items-center gap-2">
                                <Calendar className="w-4 h-4 text-blue-600" />
                                Chu kỳ thanh toán dự kiến
                              </span>
                              <span className="text-[10px] font-black text-white bg-blue-600 px-3 py-1 rounded-full shadow-sm">
                                End: {alignedPaymentCycles.endDate}
                              </span>
                            </div>
                            
                            <div className="max-h-[220px] overflow-y-auto pr-1 custom-scrollbar">
                              <table className="w-full text-left border-separate border-spacing-y-1.5">
                                <thead>
                                  <tr className="text-[10px] font-black text-slate-400 uppercase border-b border-slate-100">
                                    <th className="pb-2 pl-1">Kỳ</th>
                                    <th className="pb-2">Thời gian thanh toán</th>
                                    <th className="pb-2 text-right">Số tiền dự kiến</th>
                                  </tr>
                                </thead>
                                <tbody className="text-[10.5px]">
                                  {/* eslint-disable-next-line @typescript-eslint/no-explicit-any */}
                                  {alignedPaymentCycles.cycles.map((cycle: any) => (
                                    <tr key={cycle.index} className={`group ${cycle.is_partial ? 'bg-indigo-50 border-2 border-indigo-200' : 'bg-slate-50 border border-slate-100'} rounded-xl overflow-hidden hover:scale-[1.01] transition-all`}>
                                      <td className="p-3 rounded-l-xl font-black text-slate-500 group-hover:text-blue-700">
                                        #{cycle.index}
                                      </td>
                                      <td className="p-3 font-bold text-slate-700">
                                        <div className="flex flex-col gap-0.5">
                                          <span className="text-[11px] text-slate-900">{cycle.start}</span>
                                          <span className="text-[9px] text-slate-400 font-bold">đến {cycle.end}</span>
                                        </div>
                                      </td>
                                      <td className="p-3 rounded-r-xl text-right font-black text-slate-900 text-[11.5px]">
                                        {formatCurrency(cycle.amount)}
                                        {cycle.is_partial && (
                                          <div className="text-[8px] text-indigo-500 font-black uppercase mt-0.5">Kỳ lẻ dồn</div>
                                        )}
                                      </td>
                                    </tr>
                                  ))}
                                </tbody>
                              </table>
                            </div>
                          </div>
                        )}

                        {/* 3. THÔNG TIN ĐỐI SOÁT TÀI KHOẢN BANK */}
                        <div className={`p-3 rounded-xl border text-xs font-bold space-y-1 text-left ${selectedSite.banking_info?.is_owner_match ? 'bg-emerald-50/50 border-emerald-200 text-emerald-800' : 'bg-rose-50/50 border-rose-200 text-rose-800'}`}>
                          <div className="font-black text-[10.5px]">
                            💳 CHI TIẾT TÀI KHOẢN BANK: {selectedSite.banking_info?.is_owner_match ? '✅ TRÙNG KHỚP' : '⚠️ LỆCH CHỦ THỂ'}
                          </div>
                          <div className="text-[10px] text-slate-600 font-bold space-y-0.5 mt-1">
                            <div>🏦 <span className="text-slate-400 font-semibold">Ngân hàng:</span> <span className="text-slate-800 font-black">{selectedSite.banking_info?.bank_name} - {selectedSite.banking_info?.bank_branch}</span></div>
                            <div>🔢 <span className="text-slate-400 font-semibold">Số TK:</span> <span className="text-slate-800 font-black">{selectedSite.banking_info?.account_no}</span></div>
                            <div>👤 <span className="text-slate-400 font-semibold">Chủ TK:</span> <span className="text-slate-800 font-black">{selectedSite.banking_info?.account_owner}</span></div>
                          </div>
                        </div>

                      </div>

                      {/* CHỌN PHIẾU ĐIỀU CHỈNH & TIẾN ĐỘ */}
                      <div className="space-y-3">
                        {/* Dropbox chọn mẫu biểu mẫu */}
                        <div className="space-y-1">
                          <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block text-left">
                            📁 1. Chọn file Word (.docx) cần xuất:
                          </label>
                          <div className="relative text-left">
                            <select 
                              value={editTemplate}
                              onChange={(e) => setEditTemplate(e.target.value)}
                              className="w-full bg-slate-50 border border-slate-200 text-xs font-black text-slate-700 rounded-xl px-3 py-2.5 appearance-none focus:outline-none focus:border-blue-500 cursor-pointer shadow-sm focus:bg-white"
                            >
                              {TEMPLATE_CONFIGS.map(t => {
                                return (
                                  <option key={t.id} value={t.id}>
                                    {t.name} {!t.ready && '(Đang phát triển)'}
                                  </option>
                                );
                              })}
                            </select>
                            <ChevronDown className="absolute right-3.5 top-3 w-4 h-4 text-slate-400 pointer-events-none" />
                          </div>
                        </div>

                        {/* Dropbox cập nhật tiến độ */}
                        <div className="space-y-1">
                          <label className="text-[10px] font-black text-blue-600 uppercase tracking-widest block text-left">
                            ⚙️ 2. Trạng thái tiến độ thực tế:
                          </label>
                          <div className="relative text-left">
                            <select 
                              value={editStatus}
                              onChange={(e) => setEditStatus(e.target.value)}
                              className="w-full bg-blue-50/50 border border-blue-200 text-xs font-black text-blue-700 rounded-xl px-3 py-2.5 appearance-none focus:outline-none focus:border-blue-500 cursor-pointer shadow-sm focus:bg-white"
                            >
                              {STATUS_CATEGORIES.map(cat => (
                                <option key={cat.id} value={cat.id} className="text-slate-800 font-semibold">
                                  {cat.name}
                                </option>
                              ))}
                            </select>
                            <ChevronDown className="absolute right-3.5 top-3 w-4 h-4 text-blue-500 pointer-events-none" />
                          </div>
                        </div>
                      </div>

                      {/* PHẦN ĐIỀN THÔNG TIN THỰC TẾ ĐỂ ĐƯA VÀO BÁO CÁO THỐNG KÊ */}
                      <div className="border-t border-slate-100 pt-3 space-y-3">
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block text-left">
                          📝 3. Cập nhật số liệu đàm phán chốt:
                        </span>

                        {/* Nếu là Gia hạn hợp đồng */}
                        {(editTemplate === 'thanh_ly_ky_lai' || editTemplate === 'phu_luc_gia_han' || editStatus === 'gia_han_5_nam') && (
                          <div className="grid grid-cols-2 gap-2 bg-slate-50 p-2.5 rounded-xl border border-slate-200/50 text-left">
                            <div className="space-y-1">
                              <label className="text-[9px] font-black text-slate-500 uppercase">Số HĐ Gia Hạn Mới:</label>
                              <input 
                                type="text"
                                value={newContractNo}
                                onChange={e => setNewContractNo(e.target.value)}
                                placeholder="Số HĐ / PL mới..."
                                className="w-full bg-white text-xs text-slate-700 p-1.5 rounded border border-slate-200 focus:outline-none focus:border-blue-500"
                              />
                            </div>
                            <div className="space-y-1">
                              <label className="text-[9px] font-black text-slate-500 uppercase">Ngày Ký Mới:</label>
                              <input 
                                type="text"
                                value={newContractDate}
                                onChange={e => setNewContractDate(e.target.value)}
                                placeholder="ngày/tháng/năm..."
                                className="w-full bg-white text-xs text-slate-700 p-1.5 rounded border border-slate-200 focus:outline-none focus:border-blue-500"
                              />
                            </div>
                          </div>
                        )}

                        {/* Nếu là giảm giá thuê */}
                        {(editTemplate === 'phu_luc_giam_gia' || editTemplate === 'thanh_ly_ky_lai' || editStatus === 'dong_y') && (
                          <div className="space-y-1 bg-slate-50 p-2.5 rounded-xl border border-slate-200/50 text-left">
                            <label className="text-[9px] font-black text-slate-500 uppercase">Đơn giá mới sau đàm phán (VND):</label>
                            <div className="relative">
                              <input 
                                type="text"
                                value={newPriceConfirmed}
                                onChange={e => setNewPriceConfirmed(e.target.value)}
                                placeholder="Nhập số tiền..."
                                className="w-full bg-white text-xs font-black text-emerald-600 p-2 rounded border border-slate-200 focus:outline-none focus:border-blue-500"
                              />
                              {newPriceConfirmed && !isNaN(parseFloat(newPriceConfirmed)) && (
                                <span className="absolute right-2 top-2 text-[9px] text-slate-400 font-extrabold">
                                  {formatCurrency(parseFloat(newPriceConfirmed))}
                                </span>
                              )}
                            </div>
                          </div>
                        )}

                        {/* Nút lưu thủ công */}
                        <button
                          onClick={saveChangesToServer}
                          disabled={savingProgress}
                          className="w-full py-2.5 bg-indigo-600 hover:bg-indigo-700 text-white text-[10px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer shadow-sm active:scale-98"
                        >
                          {savingProgress ? 'Đang lưu trữ...' : '💾 Lưu tiến độ & số liệu chốt'}
                        </button>
                      </div>

                      {/* TIẾN TRÌNH TRÌNH KÝ CHECKLIST */}
                      <div className="space-y-1.5 pt-2 border-t border-slate-100 text-left">
                        <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">
                          📋 4. Checklist tiến độ {(editStatus === 'can_thanh_ly' || editStatus === 'gia_han_5_nam') ? 'Hợp Đồng Mới' : 'Phụ Lục Giảm Giá'}:
                        </span>
                        <div className="grid grid-cols-2 gap-2">
                          <button 
                            onClick={() => toggleStep('draft_prepared')}
                            className={`p-2 rounded-lg border text-left flex flex-col justify-between transition-all cursor-pointer ${selectedSite.progress_tracker.progress.draft_prepared ? 'bg-emerald-50/50 border-emerald-300 text-emerald-800' : 'bg-slate-50 border-slate-200'}`}
                          >
                            <span className="text-[9px] text-slate-400 font-extrabold uppercase">Bước 1</span>
                            <span className="text-[10px] font-extrabold text-slate-800 mt-1">Đã soạn {(editStatus === 'can_thanh_ly' || editStatus === 'gia_han_5_nam') ? 'Word HĐ' : 'Word PL'}</span>
                          </button>

                          <button 
                            onClick={() => toggleStep('submitted_internal')}
                            className={`p-2 rounded-lg border text-left flex flex-col justify-between transition-all cursor-pointer ${selectedSite.progress_tracker.progress.submitted_internal ? 'bg-emerald-50/50 border-emerald-300 text-emerald-800' : 'bg-slate-50 border-slate-200'}`}
                          >
                            <span className="text-[9px] text-slate-400 font-extrabold uppercase">Bước 2</span>
                            <span className="text-[10px] font-extrabold text-slate-800 mt-1">Trình Ký {(editStatus === 'can_thanh_ly' || editStatus === 'gia_han_5_nam') ? 'HĐ' : 'PL'}</span>
                          </button>

                          <button 
                            onClick={() => toggleStep('signed_and_stamped')}
                            className={`p-2 rounded-lg border text-left flex flex-col justify-between transition-all cursor-pointer ${selectedSite.progress_tracker.progress.signed_and_stamped ? 'bg-blue-50/50 border-blue-300 text-blue-800' : 'bg-slate-50 border-slate-200'}`}
                          >
                            <span className="text-[9px] text-slate-400 font-extrabold uppercase">Bước 3</span>
                            <span className="text-[10px] font-extrabold text-slate-800 mt-1">Đã ký Bên A-B</span>
                          </button>

                          <button 
                            onClick={() => toggleStep('archived_doc')}
                            className={`p-2 rounded-lg border text-left flex flex-col justify-between transition-all cursor-pointer ${selectedSite.progress_tracker.progress.archived_doc ? 'bg-indigo-50/50 border-indigo-300 text-indigo-800' : 'bg-slate-50 border-slate-200'}`}
                          >
                            <span className="text-[9px] text-slate-400 font-extrabold uppercase">Bước 4</span>
                            <span className="text-[10px] font-extrabold text-slate-800 mt-1">Lưu văn thư</span>
                          </button>
                        </div>
                      </div>

                      {/* THAO TÁC ENGINE WORD TỰ ĐỘNG Ở DƯỚI PANEL */}
                      <div className="border-t border-slate-100 pt-3.5 mt-2 flex items-center justify-between">
                        <div className="text-left">
                          <span className="text-[10px] text-slate-400 font-bold block">Engine điền mẫu:</span>
                          <span className="text-[11px] font-black text-slate-800 uppercase tracking-wider">Run-Preserving V4</span>
                        </div>
                        
                        <div className="flex gap-1.5">
                          <button
                            onClick={handleGenerate}
                            disabled={generating || !['thanh_ly_ky_lai', 'phu_luc_giam_gia', 'phu_luc_gia_han', 'phu_luc_giam_gia_gia_han'].includes(editTemplate)}
                            className={`px-3 py-2 text-[10px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer shadow-sm ${['thanh_ly_ky_lai', 'phu_luc_giam_gia', 'phu_luc_gia_han', 'phu_luc_giam_gia_gia_han'].includes(editTemplate) ? 'bg-emerald-500 hover:bg-emerald-600 text-white active:scale-95 shadow-emerald-500/10' : 'bg-slate-100 text-slate-400 cursor-not-allowed border border-slate-200/50'}`}
                          >
                            {generating ? 'Đang tạo...' : 'Sinh Tệp Word'}
                          </button>
                          {downloadFilename && (
                            <a
                              href={`/api/download/${downloadFilename}`}
                              download
                              className="px-3 py-2 text-[10px] font-black uppercase tracking-wider bg-blue-600 hover:bg-blue-700 text-white rounded-xl transition-all shadow flex items-center gap-1 active:scale-95 shadow-blue-500/10 animate-bounce"
                            >
                              <Download className="w-3.5 h-3.5" />
                              Tải Về (.docx)
                            </a>
                          )}
                        </div>
                      </div>

                    </div>
                  ) : (
                    <div className="flex-1 flex flex-col items-center justify-center text-center p-6 text-slate-400 font-bold text-xs space-y-2">
                      <Layers className="w-8 h-8 text-slate-300" />
                      <span>Chọn một trạm từ danh sách đối soát bên trái để bắt đầu hiệu chỉnh và soạn tệp tự động!</span>
                    </div>
                  )}

                </div>
              </>
            )}

            {/* VIEW 2: BÁO CÁO THỐNG KÊ (BIỂU ĐỒ VÀ PHÂN TÍCH THEO TỔ VT) */}
            {activeMenu === 'Báo cáo thống kê' && (
              <div className="flex-1 overflow-y-auto p-8 space-y-6">
                <div>
                  <h2 className="text-base font-black text-slate-800 uppercase tracking-wider flex items-center gap-2">
                    <BarChart2 className="w-5 h-5 text-blue-600" />
                    Biểu Đồ Tiến Độ Đàm Phán Theo Tổ Viễn Thông
                  </h2>
                  <p className="text-[11px] text-slate-400 mt-1">Thống kê phân rã tỷ lệ ký phụ lục hợp đồng, gia hạn và đàm phán giảm giá chi tiết cho từng Tổ VT tỉnh Đồng Nai</p>
                </div>

                {/* Dashboard Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                  <div className="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm text-left">
                    <span className="text-[10px] font-black text-slate-400 uppercase tracking-widest">Tỷ lệ hoàn thành toàn tỉnh</span>
                    <div className="flex items-baseline gap-2 mt-2">
                      <span className="text-2xl font-black text-blue-600">
                        {Math.round((sites.filter(isCompleted).length / sites.length) * 100) || 0}%
                      </span>
                      <span className="text-[10px] font-extrabold text-slate-400">({sites.filter(isCompleted).length}/{sites.length} trạm)</span>
                    </div>
                    <div className="w-full bg-slate-100 h-1.5 rounded-full mt-3 overflow-hidden">
                      <div className="bg-blue-600 h-full rounded-full" style={{ width: `${(sites.filter(isCompleted).length / sites.length) * 100}%` }} />
                    </div>
                  </div>

                  <div className="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm text-left">
                    <span className="text-[10px] font-black text-rose-500 uppercase tracking-widest">Cần Gia Hạn, Tái Ký</span>
                    <div className="flex items-baseline gap-2 mt-2">
                      <span className="text-2xl font-black text-rose-600">{sites.filter(isContractExpired).length}</span>
                      <span className="text-[10px] font-extrabold text-slate-400">trạm chưa gia hạn</span>
                    </div>
                    <p className="text-[9px] text-rose-400 font-bold mt-3">⚠️ Cần gia hạn, tái ký hợp đồng</p>
                  </div>

                  <div className="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm text-left">
                    <span className="text-[10px] font-black text-amber-500 uppercase tracking-widest">Chưa Làm Phụ Lục (1245)</span>
                    <div className="flex items-baseline gap-2 mt-2">
                      <span className="text-2xl font-black text-amber-600">{sites.filter(isPriceAddendumPending).length}</span>
                      <span className="text-[10px] font-extrabold text-slate-400">trạm chưa làm PL</span>
                    </div>
                    <p className="text-[9px] text-amber-400 font-bold mt-3">⚙️ Áp dụng đơn giá giảm theo 1245</p>
                  </div>

                  <div className="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm text-left">
                    <span className="text-[10px] font-black text-orange-500 uppercase tracking-widest">Lệch Tài Khoản</span>
                    <div className="flex items-baseline gap-2 mt-2">
                      <span className="text-2xl font-black text-orange-600">{sites.filter(isBankAccountMismatch).length}</span>
                      <span className="text-[10px] font-extrabold text-slate-400">trạm lệch chủ bank</span>
                    </div>
                    <p className="text-[9px] text-orange-400 font-bold mt-3">⚖️ Bổ sung giấy ủy quyền thanh toán</p>
                  </div>

                  <div className="bg-white p-5 rounded-2xl border border-slate-200/60 shadow-sm text-left">
                    <span className="text-[10px] font-black text-indigo-500 uppercase tracking-widest">Tỷ Lệ Đạt Mục Tiêu</span>
                    <div className="flex items-baseline gap-2 mt-2">
                      <span className="text-2xl font-black text-indigo-600">{targetStats.pct}%</span>
                      <span className="text-[10px] font-extrabold text-slate-400">({targetStats.reached}/{targetStats.total} đàm phán)</span>
                    </div>
                    <div className="w-full bg-slate-100 h-1.5 rounded-full mt-3 overflow-hidden">
                      <div className="bg-indigo-600 h-full rounded-full" style={{ width: `${targetStats.pct}%` }} />
                    </div>
                  </div>
                </div>

                {/* Tổ VT Breakdown Table */}
                <div className="bg-white rounded-2xl border border-slate-200 p-6 shadow-sm">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xs font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                      📊 Bảng thống kê chi tiết theo Tổ Viễn Thông (Tổ VT)
                    </h3>
                    <span className="text-[10px] text-blue-600 font-black italic">
                      💡 Riêng Tổ VT3: Trình ký phụ lục chưa được tính là Hoàn Thành
                    </span>
                  </div>
                  
                  <div className="overflow-x-auto">
                    <table className="w-full text-left border-collapse text-xs">
                      <thead>
                        <tr className="border-b border-slate-200 bg-slate-50/50 text-[10px] font-black text-slate-500 uppercase tracking-widest">
                          <th className="p-3.5 pl-5">Tên Tổ VT</th>
                          <th className="p-3.5 text-center">Tổng Số Trạm</th>
                          <th className="p-3.5 text-center text-rose-500">Cần Gia Hạn, Tái Ký</th>
                          <th className="p-3.5 text-center text-amber-500">Chưa Làm Phụ Lục (1245)</th>
                          <th className="p-3.5 text-center text-orange-500">Lệch Tài Khoản</th>
                          <th className="p-3.5 text-center text-emerald-500">Đã Hoàn Thành</th>
                          <th className="p-3.5 pl-6" style={{ width: '220px' }}>Tỷ Lệ Đạt Mục Tiêu</th>
                        </tr>
                      </thead>
                      <tbody className="divide-y divide-slate-100 font-bold text-slate-700">
                        {vtStats.map(vt => (
                          <tr key={vt.name} className="hover:bg-slate-50/60 transition-colors">
                            <td className="p-3.5 pl-5 text-slate-900 font-black flex items-center gap-2">
                              <span className="w-2.5 h-2.5 bg-blue-500 rounded-md" />
                              {vt.name}
                            </td>
                            <td className="p-3.5 text-center text-slate-800 font-black">{vt.total}</td>
                            <td className="p-3.5 text-center text-rose-600">{vt.expired}</td>
                            <td className="p-3.5 text-center text-amber-600">{vt.unaddended}</td>
                            <td className="p-3.5 text-center text-orange-600">{vt.mismatch}</td>
                            <td className="p-3.5 text-center text-emerald-600">{vt.success}</td>
                            <td className="p-3.5 pl-6">
                              <div className="flex items-center gap-2">
                                <div className="flex-1 bg-slate-100 h-2 rounded-full overflow-hidden">
                                  <div 
                                    className={`h-full rounded-full transition-all duration-500 ${vt.pct > 70 ? 'bg-emerald-500' : vt.pct > 40 ? 'bg-blue-500' : 'bg-rose-500'}`} 
                                    style={{ width: `${vt.pct}%` }} 
                                  />
                                </div>
                                <span className="text-[10px] font-black text-slate-600" style={{ minWidth: '32px' }}>{vt.pct}%</span>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </div>
            )}

            {/* VIEW 3: CÀI ĐẶT HỆ THỐNG (GOOGLE SHEETS INTEGRATION) */}
            {activeMenu === 'Cài đặt hệ thống' && (
              <div className="flex-1 overflow-y-auto p-8 flex gap-8">
                
                {/* Panel Trái: Cấu hình */}
                <div className="w-1/2 bg-white rounded-2xl border border-slate-200 p-6 shadow-sm space-y-5 h-max">
                  <div>
                    <h2 className="text-sm font-black text-slate-800 uppercase tracking-wider flex items-center gap-1.5">
                      <Settings className="w-4 h-4 text-blue-600" />
                      Cấu hình liên kết Google Sheets trực tuyến
                    </h2>
                    <p className="text-[10px] text-slate-400 mt-1">Kết nối ứng dụng với bảng tính Google Sheets để tổ công tác cập nhật tiến độ trực tuyến song song</p>
                  </div>

                  <div className="space-y-4">
                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-slate-400 uppercase tracking-widest block">Google Spreadsheet ID:</label>
                      <input 
                        type="text"
                        value={spreadsheetId}
                        onChange={e => setSpreadsheetId(e.target.value)}
                        placeholder="Nhập ID từ đường dẫn Google Sheets..."
                        className="w-full bg-slate-50 border border-slate-200 text-xs font-bold text-slate-700 rounded-xl px-3 py-2.5 focus:outline-none focus:border-blue-500 focus:bg-white transition-all shadow-inner"
                      />
                      <p className="text-[9px] text-slate-400 italic">Ví dụ URL: https://docs.google.com/spreadsheets/d/<span className="text-indigo-600 font-bold">SPREADSHEET_ID</span>/edit</p>
                    </div>

                    <div className="space-y-1.5">
                      <label className="text-[10px] font-black text-blue-600 uppercase tracking-widest block">Google Apps Script Web App URL (Sync Online):</label>
                      <input 
                        type="text"
                        value={webAppUrl}
                        onChange={e => setWebAppUrl(e.target.value)}
                        placeholder="Nhập link Web App sau khi Deploy Apps Script..."
                        className="w-full bg-blue-50/20 border border-blue-200 text-xs font-bold text-blue-700 rounded-xl px-3 py-2.5 focus:outline-none focus:border-blue-500 focus:bg-white transition-all shadow-inner"
                      />
                      <p className="text-[9px] text-blue-600 italic">Đường dẫn Apps Script triển khai dạng ứng dụng Web có quyền truy cập "Anyone".</p>
                    </div>

                    <div className="flex gap-3 pt-2">
                      <button
                        onClick={handleSaveSettings}
                        disabled={savingSettings}
                        className="flex-1 py-2.5 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white text-[10px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer shadow active:scale-98"
                      >
                        {savingSettings ? 'Đang lưu trữ...' : 'Lưu Cài Đặt Kết Nối'}
                      </button>
                      <button
                        onClick={() => {
                          fetchSitesList();
                          alert('Đang tải lại dữ liệu từ Google Sheets!');
                        }}
                        className="px-4 py-2.5 bg-slate-100 hover:bg-slate-200 border border-slate-200 text-slate-700 text-[10px] font-black uppercase tracking-wider rounded-xl transition-all cursor-pointer active:scale-98"
                      >
                        Đồng Bộ Ngay
                      </button>
                    </div>
                  </div>
                </div>

                {/* Panel Phải: Hướng dẫn tích hợp trong 2 phút */}
                <div className="w-1/2 bg-[#0F172A] rounded-2xl p-6 shadow-xl text-white space-y-4 overflow-y-auto max-h-[600px] border border-slate-800">
                  <div className="flex items-center gap-2 pb-3 border-b border-slate-800">
                    <ExternalLink className="w-4 h-4 text-emerald-400" />
                    <h3 className="text-xs font-black uppercase tracking-wider text-emerald-400">Hướng dẫn Tích hợp Google Sheets trực tuyến</h3>
                  </div>

                  <div className="space-y-3.5 text-[11px] font-medium text-slate-300 leading-relaxed">
                    <p className="font-extrabold text-white text-xs">Thực hiện các bước cực kỳ dễ dàng sau để bật đồng bộ trực tuyến:</p>
                    
                    <ol className="list-decimal pl-5 space-y-2 text-[10px]">
                      <li>Mở Google Sheets của bạn. Đảm bảo sheet có các tab tên: <span className="text-white font-extrabold">"hopdong"</span> và <span className="text-white font-extrabold">"tien do"</span>.</li>
                      <li>Vào menu <span className="text-emerald-400 font-extrabold">Mở rộng (Extensions)</span> → nhấp chọn <span className="text-emerald-400 font-extrabold">Apps Script</span>.</li>
                      <li>Xóa toàn bộ mã mặc định hiện có, sao chép toàn bộ khối mã code màu xám bên dưới và dán vào.</li>
                      <li>Nhấp vào nút <span className="text-white font-extrabold">Triển khai (Deploy)</span> (góc phải trên) → chọn <span className="text-white font-extrabold">Triển khai mới (New deployment)</span>.</li>
                      <li>Nhấp biểu tượng bánh răng ở loại triển khai, chọn <span className="text-white font-extrabold">Ứng dụng web (Web app)</span>.</li>
                      <li>Đặt cấu hình: 
                        <ul className="list-disc pl-5 mt-1 space-y-0.5 text-slate-400">
                          <li>Thực thi dưới dạng: <span className="text-white font-semibold">Tôi (Execute as: Me)</span></li>
                          <li>Ai có quyền truy cập: <span className="text-emerald-400 font-extrabold">Mọi người (Anyone)</span></li>
                        </ul>
                      </li>
                      <li>Nhấn nút **Triển khai**, nhấp **Cấp quyền truy cập (Authorize access)**, chọn tài khoản Google của bạn và nhấn **Allow (Cho phép)**.</li>
                      <li>Sao chép **URL Ứng dụng web (Web app URL)** và dán vào ô nhập liệu màu xanh bên trái!</li>
                    </ol>

                    <div className="pt-2">
                      <div className="flex justify-between items-center mb-1 bg-slate-800 px-3 py-1.5 rounded-t-lg">
                        <span className="text-[9px] uppercase font-black text-slate-400">Mã nguồn Google Apps Script:</span>
                        <button 
                          onClick={() => {
                            navigator.clipboard.writeText(appsScriptCode);
                            alert('Đã sao chép đoạn mã Apps Script vào bộ nhớ tạm!');
                          }}
                          className="flex items-center gap-1 text-[9px] font-black uppercase text-emerald-400 hover:text-emerald-300 transition-colors cursor-pointer"
                        >
                          <Copy className="w-3 h-3" />
                          Sao chép code
                        </button>
                      </div>
                      <pre className="bg-[#1E293B] text-[8.5px] p-3 rounded-b-lg overflow-x-auto max-h-[180px] border border-slate-800 text-slate-400 font-mono text-left leading-relaxed">
                        {appsScriptCode}
                      </pre>
                    </div>
                  </div>
                </div>

              </div>
            )}

          </div>
        )}

      </div>
    </div>
  )
}

export default App
