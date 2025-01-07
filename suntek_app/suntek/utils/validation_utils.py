import re


def validate_mobile_number(number):
    number = str(number)
    pattern = r"^(\+91[-]?)?[6-9]\d{9}$"
    if re.match(pattern, number):
        return True
    else:
        return False


def extract_first_and_last_name(name: str):
    if not name:
        return "", "", ""

    name_parts = [part for part in name.strip().split() if part]

    if len(name_parts) == 1:
        return name_parts[0], "", ""
    elif len(name_parts) == 2:
        return name_parts[0], "", name_parts[1]
    else:
        first_name = name_parts[0]
        last_name = name_parts[-1]
        middle_name = " ".join(name_parts[1:-1])
        return first_name, middle_name, last_name


def convert_date_format(date_str):
    """Convert date from dd-mm-yyyy to yyyy-mm-dd"""
    if not date_str:
        return None
    try:
        day, month, year = date_str.split("-")
        return f"{year}-{month}-{day}"
    except Exception:
        return None
