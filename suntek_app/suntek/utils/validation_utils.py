import datetime
import re


def validate_mobile_number(number):
    """Validate mobile number. It should be 10 digits and start with 6-9"""
    number = str(number)
    pattern = r"^(\+91[-]?)?[6-9]\d{9}$"
    if re.match(pattern, number):
        return True
    else:
        return False


def extract_first_and_last_name(name: str):
    """Extract first, middle and last name from full name"""
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


def convert_date_format(text):
    """Convert dd-mm-yyyy to yyyy-mm-dd"""
    pattern = r"(\d{2})-(\d{2})-(\d{4})"

    converted_text = re.sub(pattern, r"\3-\2-\1", text)

    return converted_text


def format_date(date_string):
    """Convert date string to YYYY-MM-DD format"""
    if not date_string:
        return None
    try:
        # First check if it's already in YYYY-MM-DD format
        if "-" in date_string and len(date_string.split("-")[0]) == 4:
            return date_string

        # Handle DD-MM-YYYY format
        if "-" in date_string:
            day, month, year = date_string.split("-")
        elif "/" in date_string:
            day, month, year = date_string.split("/")
        else:
            return None

        # Convert to datetime and then to string in correct format
        date_obj = datetime.datetime(int(year), int(month), int(day))
        return date_obj.strftime("%Y-%m-%d")
    except Exception:
        return None
