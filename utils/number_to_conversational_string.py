def convert_number_to_conversational(num: int | str) -> str:
    # Mapping of digits to words
    digit_map = {
        '0': 'zero',
        '1': 'one',
        '2': 'two',
        '3': 'three',
        '4': 'four',
        '5': 'five',
        '6': 'six',
        '7': 'seven',
        '8': 'eight',
        '9': 'nine',
        '+': 'plus'
    }
    
    num_str = str(num).strip()
    result = []
    i = 0

    while i < len(num_str):
        ch = num_str[i]
        
        # Count consecutive same digits
        count = 1
        while i + count < len(num_str) and num_str[i + count] == ch:
            count += 1
        
        if ch in digit_map:
            if count == 1:
                result.append(digit_map[ch])
            elif count == 2:
                result.append(f"double {digit_map[ch]}")
            elif count == 3:
                result.append(f"triple {digit_map[ch]}")
            elif count == 4:
                result.append(f"double {digit_map[ch]} double {digit_map[ch]}")
            elif count == 5:
                result.append(f"five times {digit_map[ch]}")
            elif count == 6:
                result.append(f"six times {digit_map[ch]}")
            elif count == 7:
                result.append(f"seven times {digit_map[ch]}")
            elif count == 8:
                result.append(f"eight times {digit_map[ch]}")
            elif count == 9:
                result.append(f"nine time {digit_map[ch]}")
            elif count == 10:
                result.append(f"ten times {digit_map[ch]}")
            else:
                result.extend([digit_map[ch]] * count)
        else:
            result.append(ch)  # For unexpected characters
        
        i += count
    
    result = ' '.join(result)
    # result = result + ' ' + f"({str(num)})"
    return result


if __name__ == "__main__":
    print(convert_number_to_conversational("+9194509297777771"))
