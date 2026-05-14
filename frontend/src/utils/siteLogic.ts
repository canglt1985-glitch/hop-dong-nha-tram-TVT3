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

export const calculateAlignedCycles = (startDateStr: string, cycleMonths: number, termYears: number, monthlyPrice: number) => {
  const [day, month, year] = startDateStr.split('/').map(Number);
  const startDate = new Date(year, month - 1, day);
  
  if (isNaN(startDate.getTime())) return null;

  // 1. Calculate Contract End Date (Standardized logic)
  const isExactMonthStart = day === 1;
  const endYear = year + termYears;
  
  let finalContractEnd: Date;
  if (isExactMonthStart) {
    // Ví dụ: Bắt đầu 01/06/2026 -> 5 năm sau kết thúc 31/05/2031 (Tròn 60 tháng)
    finalContractEnd = new Date(endYear, month - 1, 0); 
  } else {
    // Ví dụ: Bắt đầu 09/04/2026 -> 5 năm sau kết thúc 30/04/2031 (60 tháng + ngày lẻ)
    finalContractEnd = new Date(endYear, month, 0);
  }

  // eslint-disable-next-line @typescript-eslint/no-explicit-any
  const cycles: any[] = [];
  
  // Cycle 1: Align to end of month after cycleMonths
  // Logic: 
  // - Nếu bắt đầu ngày 1: Kỳ 1 tròn cycleMonths (VD: 01/05 -> 31/10)
  // - Nếu bắt đầu ngày lẻ: Kỳ 1 = ngày lẻ + cycleMonths (VD: 09/04 -> 31/10)
  const c1EndMonthIndex = isExactMonthStart ? (month - 1 + cycleMonths - 1) : (month - 1 + cycleMonths);
  const c1EndDate = new Date(year, c1EndMonthIndex + 1, 0); // Last day of month

  // Calculate Cycle 1 Price
  const daysInStartMonth = new Date(year, month, 0).getDate();
  const daysWorkedInStartMonth = daysInStartMonth - day + 1;
  
  let c1Total = 0;
  if (isExactMonthStart) {
    c1Total = Math.round(monthlyPrice * cycleMonths);
  } else {
    const c1PricePartial = (monthlyPrice / 30) * daysWorkedInStartMonth;
    const c1PriceFull = monthlyPrice * cycleMonths;
    c1Total = Math.round(c1PricePartial + c1PriceFull);
  }
  
  cycles.push({
    index: 1,
    start: startDateStr,
    end: c1EndDate.toLocaleDateString('en-GB'),
    amount: c1Total,
    is_partial: true
  });
  
  // Subsequent Cycles: Start from next day, exactly cycleMonths
  let nextStart = new Date(c1EndDate);
  nextStart.setDate(nextStart.getDate() + 1);
  
  let idx = 2;
  while (nextStart < finalContractEnd) {
    const targetEndMonthIndex = nextStart.getMonth() + cycleMonths - 1;
    let cEndDate = new Date(nextStart.getFullYear(), targetEndMonthIndex + 1, 0);
    
    let cTotal = monthlyPrice * cycleMonths;
    
    // Check if we exceed contract end
    if (cEndDate > finalContractEnd) {
      cEndDate = new Date(finalContractEnd);
      // Calculate months diff
      const monthsDiff = (cEndDate.getFullYear() - nextStart.getFullYear()) * 12 + (cEndDate.getMonth() - nextStart.getMonth()) + 1;
      cTotal = monthlyPrice * monthsDiff;
    }
    
    cycles.push({
      index: idx,
      start: nextStart.toLocaleDateString('en-GB'),
      end: cEndDate.toLocaleDateString('en-GB'),
      amount: Math.round(cTotal),
      is_partial: false
    });
    
    nextStart = new Date(cEndDate);
    nextStart.setDate(nextStart.getDate() + 1);
    idx++;
  }
  
  return {
    startDate: startDateStr,
    endDate: finalContractEnd.toLocaleDateString('en-GB'),
    cycles
  };
};

