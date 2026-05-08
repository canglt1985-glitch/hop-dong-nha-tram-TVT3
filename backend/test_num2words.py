# Test converting number to Vietnamese words
def num_to_words_vn(n):
    """Convert integer to Vietnamese words - simple version"""
    ones = ['', 'một', 'hai', 'ba', 'bốn', 'năm', 'sáu', 'bảy', 'tám', 'chín']
    tens = ['', 'mười', 'hai mươi', 'ba mươi', 'bốn mươi', 'năm mươi', 'sáu mươi', 'bảy mươi', 'tám mươi', 'chín mươi']
    
    n = int(n)
    if n == 0: return 'không'
    
    result = ''
    if n >= 1000000000:
        result += ones[n // 1000000000] + ' tỷ '
        n %= 1000000000
    if n >= 1000000:
        millions = n // 1000000
        if millions >= 10:
            result += tens[millions // 10] + ' '
            if millions % 10: result += ones[millions % 10] + ' '
        else:
            result += ones[millions] + ' '
        result += 'triệu '
        n %= 1000000
    if n >= 1000:
        thousands = n // 1000
        if thousands >= 10:
            result += tens[thousands // 10] + ' '
            if thousands % 10: result += ones[thousands % 10] + ' '
        else:
            result += ones[thousands] + ' '
        result += 'nghìn '
        n %= 1000
    if n >= 100:
        result += ones[n // 100] + ' trăm '
        n %= 100
    if n >= 10:
        result += tens[n // 10] + ' '
        n %= 10
    if n > 0:
        result += ones[n]
    return result.strip() + ' đồng'

print(num_to_words_vn(5250000))
print(num_to_words_vn(4356000))
