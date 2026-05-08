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

export const updateProgress = async (payload: any) => {
  const res = await fetch('/api/progress', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(payload)
  });
  if (!res.ok) throw new Error('Failed to update progress');
  return res.json();
};

export const generateDocument = async (siteId: string, templateType: string) => {
  const res = await fetch(`/api/generate/${siteId}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ template_type: templateType })
  });
  if (!res.ok) throw new Error('Không thể sinh mẫu văn bản này!');
  return res.json();
};
