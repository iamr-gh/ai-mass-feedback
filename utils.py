import re


def printColor(text, color):
    if color == "green":
        color_code = "\033[92m"
    elif color == "red":
        color_code = "\033[91m"
    elif color == "blue":
        color_code = "\033[94m"
    elif color == "yellow":
        color_code = "\033[93m"
    else:
        color_code = "\033[0m"

    print(color_code)
    print(text)
    print("\033[0m")


def find_highest_number_in_string(text):
    """
    Finds the highest numerical value present in a given string.

    Args:
      text: The input string that may contain numbers.

    Returns:
      The highest numerical value found in the string as an int or float,
      or None if no numbers are found.
    """
    # Use a regular expression to find all sequences of digits,
    # optionally with a decimal point.
    # r'\d+\.?\d*' matches one or more digits, optionally followed by a
    # period and then zero or more digits.

    numbers_as_strings = re.findall(r"\d+\.?\d*", text)

    if not numbers_as_strings:
        return None  # No numbers found in the string

    # Convert the found strings to numerical types (float is safer for decimals)
    numbers = []
    for num_str in numbers_as_strings:
        try:
            numbers.append(float(num_str))
        except ValueError:
            # This case should ideally not happen if the regex is robust,
            # but it's good practice to handle potential conversion errors.
            continue

    if not numbers:
        return None  # No valid numbers could be converted

    return int(max(numbers))
