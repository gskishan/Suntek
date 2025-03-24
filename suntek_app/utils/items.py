import frappe


@frappe.whitelist()
def get_item_prices(items, price_list_name="Standard Selling"):
    print(f"get_item_prices called with items: {items}, price_list: {price_list_name}")

    if not items:
        return {}

    if isinstance(items, str):
        items = frappe.parse_json(items)

    result = {}

    print(f"Processing {len(items)} items")

    for item_code in items:
        if not item_code:
            continue

        rate = frappe.db.get_value(
            "Item Price",
            {"item_code": item_code, "price_list": price_list_name, "selling": 1},
            "price_list_rate",
        )

        print(f"Item {item_code}: found rate {rate}")

        if rate:
            result[item_code] = rate

    print(f"Final result: {result}")
    return result
