import type { Site } from '../types/site';

export const formatCurrency = (val: number) => {
  return new Intl.NumberFormat('vi-VN', { style: 'currency', currency: 'VND' })
    .format(val)
    .replace('₫', 'đ');
};

export const isContractExpired = (site: Site) => {
  return site.progress_tracker?.status === 'can_thanh_ly' || site.ext_status.includes('Cần gia hạn');
};

export const isCompleted = (site: Site) => {
  if (site.no_addendum_needed) return true;
  
  const status = site.progress_tracker?.status || 'dong_y';
  
  // Áp dụng chung cho tất cả các tổ: Trình ký phụ lục trở lên đã được tính là hoàn thành
  return ['trinh_ky_phu_luc', 'gia_han_5_nam', 'da_ky_ho_so', 'da_gui_thanh_toan'].includes(status);
};

export const isPriceAddendumPending = (site: Site) => {
  const agreed1245 = site.has_agreed_1245 === true || 
                     ['dong_y', 'trinh_ky_phu_luc', 'da_ky_ho_so', 'da_gui_thanh_toan'].includes(site.progress_tracker?.status || '');
  
  if (!agreed1245) return false;
  if (isCompleted(site)) return false;
  if (site.no_addendum_needed) return false;
  
  // ⚠️ Block addendum if negotiation has not reached target
  if (site.reached_target && (site.reached_target.toLowerCase().includes('không') || site.reached_target.toLowerCase().includes('chưa'))) {
    return false;
  }

  return true;
};

export const isBankAccountMismatch = (site: Site) => {
  return site.banking_info?.is_owner_match === false;
};

export const matchToVt = (siteToVt: string, filterToVt: string) => {
  if (!siteToVt || !filterToVt) return false;
  const sVt = siteToVt.toUpperCase().trim();
  const fVt = filterToVt.toUpperCase().trim();
  
  if (sVt.includes(fVt) || fVt.includes(sVt)) return true;
  
  const filterDigit = fVt.replace(/\D/g, '');
  const siteDigit = sVt.replace(/\D/g, '');
  
  if (filterDigit && filterDigit === siteDigit) return true;
  if (filterDigit && sVt.includes(filterDigit)) return true;
  
  const vShort = 'V' + filterDigit;
  if (sVt.includes(vShort)) return true;
  
  return false;
};

export const isOutOfPriceRange = (site: Site) => {
  const isNotTarget = (site.dat_muc_tieu_1245 || '').toLowerCase().includes('không đạt') || 
                      (site.reached_target || '').toLowerCase().includes('không đạt');
  return isNotTarget;
};

export const isUnpaid = (site: Site) => {
  // Cần thanh toán: Trạm đã hoàn tất hồ sơ phụ lục nhưng status chưa phải là "da_gui_thanh_toan"
  if (!isCompleted(site)) return false;
  return site.progress_tracker?.status !== 'da_gui_thanh_toan';
};

