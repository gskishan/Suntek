import datetime
import re

import frappe
from frappe import _


def duplicate_check(doc):
    mobile_no = str(doc.mobile_no)
    sql = f"""select * from `tabLead` where mobile_no="{mobile_no}" and name!="{doc.name}" """
    data = frappe.db.sql(sql, as_dict=True)
    if data:
        frappe.throw(
            f"Duplicate mobile no {mobile_no} already linked to <b>{data[0].custom_enquiry_owner_name}</b> ",
        )


def validate_mobile_number(number):
    """Validate mobile number. It should be 10 digits and start with 6-9"""
    number = str(number)
    if " " in number:
        return False
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
        if "-" in date_string and len(date_string.split("-")[0]) == 4:
            return date_string
        if "-" in date_string:
            day, month, year = date_string.split("-")
        elif "/" in date_string:
            day, month, year = date_string.split("/")
        else:
            return None

        date_obj = datetime.datetime(int(year), int(month), int(day))
        return date_obj.strftime("%Y-%m-%d")
    except Exception:
        return None


def convert_timestamp_to_date(timestamp_ms):
    """Convert millisecond timestamp to yyyy-mm-dd format for database storage"""
    if not timestamp_ms:
        return None

    try:
        timestamp_str = str(timestamp_ms).strip()
        date_obj = datetime.datetime.fromtimestamp(float(timestamp_str) / 1000)
        return date_obj.strftime("%Y-%m-%d")
    except (ValueError, TypeError, OSError):
        return None


def validate_pan_number(pan_number):
    if pan_number and not re.match(r"^[A-Z]{5}[0-9]{4}[A-Z]{1}$", pan_number):
        frappe.throw(_("Invalid PAN Number Format"))
