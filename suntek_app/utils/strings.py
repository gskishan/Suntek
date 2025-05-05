import re


def extract_numeric_and_unit(value):
    if not value:
        return None, None

    match = re.match(r"^([\d.]+)([^\d.]*)$", str(value).strip())

    if match:
        numeric_value = float(match.group(1))
        unit = match.group(2).strip()

        return numeric_value, unit

    return None, None
