import pytest
from utils.pricing_utils import get_last_day_of_month, calculate_aligned_cycles

def test_get_last_day_of_month():
    assert get_last_day_of_month(2026, 2) == 28
    assert get_last_day_of_month(2024, 2) == 29 # Leap year
    assert get_last_day_of_month(2026, 4) == 30
    assert get_last_day_of_month(2026, 1) == 31

def test_calculate_aligned_cycles_exact_start():
    # Bắt đầu đúng ngày 01/01/2026, chu kỳ 6 tháng, hợp đồng 5 năm, giá 5tr/tháng
    res = calculate_aligned_cycles("01/01/2026", 6, 5, 5000000.0)
    
    assert res is not None
    assert "error" not in res
    assert res["start_date"] == "01/01/2026"
    assert res["end_date"] == "31/12/2030" # 5 years
    
    cycles = res["cycles"]
    assert len(cycles) == 10 # 5 years * 2 cycles/year
    
    # Kỳ 1: 01/01/2026 -> 30/06/2026
    assert cycles[0]["start"] == "01/01/2026"
    assert cycles[0]["end"] == "30/06/2026"
    assert cycles[0]["amount"] == 30000000.0
    
def test_calculate_aligned_cycles_partial_start():
    # Bắt đầu ngày lẻ 15/04/2026
    res = calculate_aligned_cycles("15/04/2026", 6, 5, 5000000.0)
    
    assert "error" not in res
    assert res["start_date"] == "15/04/2026"
    assert res["end_date"] == "30/04/2031"
    
    cycles = res["cycles"]
    
    # Kỳ 1: Cân đối ngày lẻ, kết thúc vào cuối tháng thứ 6 tính từ tháng bắt đầu
    # Start: 15/04/2026. Tháng bắt đầu: 4. + 6 tháng = tháng 10. End date = 31/10/2026.
    assert cycles[0]["start"] == "15/04/2026"
    assert cycles[0]["end"] == "31/10/2026"
