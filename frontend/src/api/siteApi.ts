export const fetchSettings = async () => {
  const res = await fetch('/api/settings');
  if (!res.ok) throw new Error('Failed to fetch settings');
  return res.json();
};

export const updateSettings = async (payload: { spreadsheet_id: string; web_app_url: string }) => {
  const res = await fetch('/api/settings', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to update settings');
  return res.json();
};

export const fetchSites = async (forceRefresh: boolean = false) => {
  const url = forceRefresh ? '/api/sites?force_refresh=true' : '/api/sites';
  const res = await fetch(url);
  if (!res.ok) throw new Error('Không thể tải dữ liệu từ backend');
  return res.json();
};

// eslint-disable-next-line @typescript-eslint/no-explicit-any
export const updateProgress = async (payload: any) => {
  const res = await fetch('/api/progress', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to update progress');
  return res.json();
};

export const generateDocument = async (
  siteId: string,
  templateType: string,
  applyVb1245: boolean = true,
  representative?: string,
  scenario?: string,
  extensionYears?: number,
  customStartDate?: string,
  pricesBreakdown?: Record<string, number>,
  newPriceConfirmed?: number
) => {
  const res = await fetch(`/api/generate/${siteId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      template_type: templateType,
      apply_vb1245: applyVb1245,
      representative,
      scenario,
      extension_years: extensionYears,
      custom_start_date: customStartDate,
      prices_breakdown: pricesBreakdown,
      new_price_confirmed: newPriceConfirmed
    })
  });
  if (!res.ok) {
    const errData = await res.json().catch(() => ({}));
    throw new Error(errData.detail || 'Không thể sinh mẫu văn bản này!');
  }
  return res.json();
};

export const generateBulkCct = async (siteIds: string[], party: 'A' | 'B' = 'B', includeExtension: boolean = false) => {
  const res = await fetch(`/api/generate-bulk-cct`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ site_ids: siteIds, party, include_extension: includeExtension })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Không thể xuất file!');
  return data;
};

export const generateBBLV = async (siteId: string, representative: string, scenario: string = "auto") => {
  const res = await fetch(`/api/generate-bblv/${siteId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ representative, scenario })
  });
  if (!res.ok) throw new Error('Không thể sinh Biên bản làm việc!');
  return res.json();
};

export const generateBulkBBLV = async (siteIds: string[], representative: string, scenario: string = "auto") => {
  const res = await fetch(`/api/generate-bulk-bblv`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ site_ids: siteIds, representative, scenario })
  });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || 'Không thể sinh Biên bản hàng loạt!');
  return data;
};
export const openFolder = async () => {
  const res = await fetch('/api/open-folder', { method: 'POST' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Không thể mở thư mục trên máy tính');
  }
  return res.json();
};

export const openFileDirectly = async (filename: string) => {
  const res = await fetch('/api/open-file', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ filename })
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Không thể mở tệp tin trực tiếp');
  }
  return res.json();
};

export const cleanOutputFolder = async () => {
  const res = await fetch('/api/clean-output', { method: 'POST' });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.detail || 'Không thể dọn dẹp thư mục');
  }
  return res.json();
};

export const downloadFileHelper = async (filename: string, askFolder: boolean = true) => {
  try {
    let cleanFilename = filename.split('/').pop() || filename;
    try {
      cleanFilename = decodeURIComponent(cleanFilename);
    } catch {
      // ignore
    }

    const downloadUrl = filename.startsWith('/') || filename.startsWith('http')
      ? filename
      : `/api/download/${encodeURIComponent(cleanFilename)}`;

    const response = await fetch(downloadUrl);
    if (!response.ok) throw new Error(`HTTP error! status: ${response.status}`);
    const blob = await response.blob();

    // 1. Trình duyệt hiện đại hỗ trợ hộp thoại Save As (ghi nhớ thư mục tải về gần nhất)
    if (askFolder && 'showSaveFilePicker' in window) {
      try {
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        const handle = await (window as any).showSaveFilePicker({
          suggestedName: cleanFilename,
          types: [
            {
              description: 'Tài liệu Word (.docx)',
              accept: {
                'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx']
              }
            }
          ]
        });
        const writable = await handle.createWritable();
        await writable.write(blob);
        await writable.close();
        return;
      } catch (pickerErr: any) {
        // Nếu người dùng bấm Cancel trên hộp thoại lưu thì hủy
        if (pickerErr.name === 'AbortError') {
          return;
        }
        console.warn('showSaveFilePicker fallback:', pickerErr);
      }
    }

    // 2. Fallback cơ chế tải chuẩn của trình duyệt
    const blobUrl = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.style.display = 'none';
    a.href = blobUrl;
    a.download = cleanFilename;
    document.body.appendChild(a);
    a.click();
    window.URL.revokeObjectURL(blobUrl);
    a.remove();
  } catch (err) {
    console.error('Lỗi download file:', err);
    window.open(`/api/download/${encodeURIComponent(filename)}`, '_blank');
  }
};

