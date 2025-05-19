import re


def clean_capacity(doc, method):
    if not doc.custom_capacity:
        return None

    capacity = str(doc.custom_capacity).strip()

    try:
        float(capacity)
        return
    except ValueError:
        pass

    cleaned_value = None
    number_match = re.search(r"(\d+(\.\d+)?)", capacity)
    if number_match:
        try:
            cleaned_value = float(number_match.group(1))
        except ValueError:
            pass

    if cleaned_value is not None:
        doc.custom_capacity = cleaned_value
    else:
        doc.custom_capacity = None
