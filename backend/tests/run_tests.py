import sys
import os

# Add backend directory to sys.path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from tests.test_data_utils import (
    test_parse_numeric_value_basic,
    test_parse_numeric_value_string,
    test_parse_numeric_value_with_currency,
    test_parse_numeric_value_complex_formats,
    test_parse_numeric_value_invalid
)

from tests.test_pricing_utils import (
    test_get_last_day_of_month,
    test_calculate_aligned_cycles_exact_start,
    test_calculate_aligned_cycles_partial_start
)

def run():
    print("Running test_data_utils...")
    test_parse_numeric_value_basic()
    test_parse_numeric_value_string()
    test_parse_numeric_value_with_currency()
    test_parse_numeric_value_complex_formats()
    test_parse_numeric_value_invalid()
    print("  -> test_data_utils: ALL PASSED")

    print("Running test_pricing_utils...")
    test_get_last_day_of_month()
    test_calculate_aligned_cycles_exact_start()
    test_calculate_aligned_cycles_partial_start()
    print("  -> test_pricing_utils: ALL PASSED")

    print("\n[SUCCESS] ALL BACKEND TESTS PASSED CLEANLY!")

if __name__ == "__main__":
    run()
