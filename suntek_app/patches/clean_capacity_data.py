import re

import frappe


def execute():
    leads = frappe.get_all("Lead", ["name", "custom_capacity"], {"custom_capacity": ["!=", None]})
    opportunities = frappe.get_all("Opportunity", ["name", "custom_capacity"], {"custom_capacity": ["!=", None]})

    updated_count = 0
    skipped_count = 0
    nullified_count = 0
    updates = []
    already_numeric = 0

    for record in leads + opportunities:
        doctype = "Lead" if record in leads else "Opportunity"
        capacity = record.get("custom_capacity")

        if not capacity:
            skipped_count += 1
            continue

        if str(capacity).strip().isdigit():
            already_numeric += 1
            continue

        cleaned_value = None
        original = str(capacity)

        try:
            try:
                cleaned_value = float(original.strip())
                if cleaned_value.is_integer():
                    cleaned_value = int(cleaned_value)
            except ValueError:
                number_match = re.search(r"(\d+(\.\d+)?)", original)
                if number_match:
                    cleaned_value = float(number_match.group(1))
                    if cleaned_value.is_integer():
                        cleaned_value = int(cleaned_value)

                elif any(char in original for char in ["&", "+", "-", "/"]):
                    for separator in ["&", "+", "-", "/"]:
                        if separator in original:
                            parts = original.split(separator, 1)
                            number_match = re.search(r"(\d+(\.\d+)?)", parts[0])
                            if number_match:
                                cleaned_value = float(number_match.group(1))
                                if cleaned_value.is_integer():
                                    cleaned_value = int(cleaned_value)
                                break

        except Exception as e:
            print(f"Error processing {doctype} {record['name']}: {str(e)}")
            skipped_count += 1
            continue

        if cleaned_value is not None:
            doc = frappe.get_doc(doctype, record["name"])
            doc.db_set("custom_capacity", str(cleaned_value))
            updates.append(
                {"doctype": doctype, "name": record["name"], "original": original, "cleaned": str(cleaned_value)}
            )
            updated_count += 1
        else:
            doc = frappe.get_doc(doctype, record["name"])
            doc.db_set("custom_capacity", None)
            nullified_count += 1
            print(f"Set to NULL: '{original}' ({doctype} {record['name']})")

    print("\nCleaning Summary:")
    print(f"Total records processed: {len(leads) + len(opportunities)}")
    print(f"Records already numeric: {already_numeric}")
    print(f"Records updated with numeric values: {updated_count}")
    print(f"Records set to NULL: {nullified_count}")
    print(f"Records skipped: {skipped_count}")

    print("\nSample of updates made (first 10):")
    for _, update in enumerate(updates[:10]):
        print(f"{update['doctype']} {update['name']}: '{update['original']}' -> '{update['cleaned']}'")

    return f"Updated {updated_count} capacity values, nullified {nullified_count}, skipped {skipped_count}, already numeric: {already_numeric}"
